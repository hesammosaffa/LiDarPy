#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include <rs_driver/api/lidar_driver.hpp>
#include <rs_driver/msg/point_cloud_msg.hpp>

#include <cmath>
#include <chrono>
#include <cstring>
#include <condition_variable>
#include <cstdint>
#include <memory>
#include <mutex>
#include <vector>

namespace py = pybind11;

class LidarSource
{
    using Cloud = ::PointCloudT<::PointXYZI>;

public:
    LidarSource(uint16_t msop = 6699, uint16_t difop = 7788)
    {
        using namespace robosense::lidar;
        RSDriverParam p;
        p.input_type = InputType::ONLINE_LIDAR;
        p.lidar_type = LidarType::RSEM4;
        p.input_param.msop_port = msop;
        p.input_param.difop_port = difop;
        p.decoder_param.wait_for_difop = false;

        driver_.regPointCloudCallback(
            [] { return std::make_shared<Cloud>(); },
            [this](std::shared_ptr<Cloud> c) {
                std::vector<float> v;
                v.reserve(c->points.size() * 3);
                for (const auto &q : c->points)
                    if (std::isfinite(q.x) && std::isfinite(q.y) && std::isfinite(q.z)) {
                        v.push_back(q.x); v.push_back(q.y); v.push_back(q.z);
                    }
                std::lock_guard<std::mutex> l(mtx_);
                pts_ = std::move(v);
                ++seq_;
                cv_.notify_all();
            });
        driver_.regExceptionCallback([](const Error &) {});

        ok_ = driver_.init(p);
        if (ok_) driver_.start();
    }

    ~LidarSource() { stop(); }

    bool ok() const { return ok_; }

    void stop()
    {
        if (ok_ && !stopped_) { driver_.stop(); stopped_ = true; }
        { std::lock_guard<std::mutex> l(mtx_); quit_ = true; }
        cv_.notify_all();
    }

    uint64_t wait(uint64_t seen, int timeout_ms)
    {
        py::gil_scoped_release rel;
        std::unique_lock<std::mutex> l(mtx_);
        cv_.wait_for(l, std::chrono::milliseconds(timeout_ms),
                     [&] { return quit_ || seq_ != seen; });
        return seq_;
    }

    py::tuple take()
    {
        std::vector<float> v;
        uint64_t s;
        {
            std::lock_guard<std::mutex> l(mtx_);
            v = pts_;
            s = seq_;
        }
        const py::ssize_t n = py::ssize_t(v.size() / 3);
        py::array_t<float> a({n, py::ssize_t(3)});
        if (n) std::memcpy(a.mutable_data(), v.data(), v.size() * sizeof(float));
        return py::make_tuple(s, a);
    }

private:
    robosense::lidar::LidarDriver<Cloud> driver_;
    std::mutex mtx_;
    std::condition_variable cv_;
    std::vector<float> pts_;
    uint64_t seq_ = 0;
    bool ok_ = false, stopped_ = false, quit_ = false;
};

PYBIND11_MODULE(rs_bridge, m)
{
    m.doc() = "RoboSense source (rs_driver) for Python";
    py::class_<LidarSource>(m, "LidarSource")
        .def(py::init<uint16_t, uint16_t>(), py::arg("msop") = 6699, py::arg("difop") = 7788)
        .def_property_readonly("ok", &LidarSource::ok)
        .def("stop", &LidarSource::stop)
        .def("wait", &LidarSource::wait, py::arg("seen"), py::arg("timeout_ms") = 100)
        .def("take", &LidarSource::take);
}
