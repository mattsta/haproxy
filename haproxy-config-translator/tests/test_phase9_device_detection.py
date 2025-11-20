"""Tests for Phase 9 Device Detection directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase9DeviceAtlas:
    """Test DeviceAtlas device detection directives."""

    def test_deviceatlas_json_file(self):
        """Test deviceatlas-json-file directive."""
        config = """
        config test {
            global {
                deviceatlas-json-file: "/etc/haproxy/deviceatlas.json"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.deviceatlas_json_file == "/etc/haproxy/deviceatlas.json"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "deviceatlas-json-file /etc/haproxy/deviceatlas.json" in output

    def test_deviceatlas_log_level(self):
        """Test deviceatlas-log-level directive."""
        config = """
        config test {
            global {
                deviceatlas-log-level: 3
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.deviceatlas_log_level == 3

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "deviceatlas-log-level 3" in output

    def test_deviceatlas_separator(self):
        """Test deviceatlas-separator directive."""
        config = """
        config test {
            global {
                deviceatlas-separator: "|"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.deviceatlas_separator == "|"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "deviceatlas-separator |" in output

    def test_deviceatlas_properties_cookie(self):
        """Test deviceatlas-properties-cookie directive."""
        config = """
        config test {
            global {
                deviceatlas-properties-cookie: "DEVICEATLAS"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.deviceatlas_properties_cookie == "DEVICEATLAS"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "deviceatlas-properties-cookie DEVICEATLAS" in output

    def test_deviceatlas_complete_configuration(self):
        """Test complete DeviceAtlas configuration."""
        config = """
        config test {
            global {
                deviceatlas-json-file: "/var/lib/deviceatlas/data.json"
                deviceatlas-log-level: 2
                deviceatlas-separator: ","
                deviceatlas-properties-cookie: "DA_PROPS"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.deviceatlas_json_file == "/var/lib/deviceatlas/data.json"
        assert ir.global_config.deviceatlas_log_level == 2
        assert ir.global_config.deviceatlas_separator == ","
        assert ir.global_config.deviceatlas_properties_cookie == "DA_PROPS"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "deviceatlas-json-file /var/lib/deviceatlas/data.json" in output
        assert "deviceatlas-log-level 2" in output
        assert "deviceatlas-separator ," in output
        assert "deviceatlas-properties-cookie DA_PROPS" in output


class TestPhase951Degrees:
    """Test 51Degrees device detection directives."""

    def test_51degrees_data_file(self):
        """Test 51degrees-data-file directive."""
        config = """
        config test {
            global {
                51degrees-data-file: "/etc/haproxy/51degrees.dat"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_data_file == "/etc/haproxy/51degrees.dat"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-data-file /etc/haproxy/51degrees.dat" in output

    def test_51degrees_property_name_list(self):
        """Test 51degrees-property-name-list directive."""
        config = """
        config test {
            global {
                51degrees-property-name-list: "BrowserName,BrowserVersion,DeviceType"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_property_name_list == "BrowserName,BrowserVersion,DeviceType"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-property-name-list BrowserName,BrowserVersion,DeviceType" in output

    def test_51degrees_property_separator(self):
        """Test 51degrees-property-separator directive."""
        config = """
        config test {
            global {
                51degrees-property-separator: ","
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_property_separator == ","

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-property-separator ," in output

    def test_51degrees_cache_size(self):
        """Test 51degrees-cache-size directive."""
        config = """
        config test {
            global {
                51degrees-cache-size: 10000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_cache_size == 10000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-cache-size 10000" in output

    def test_51degrees_complete_configuration(self):
        """Test complete 51Degrees configuration."""
        config = """
        config test {
            global {
                51degrees-data-file: "/var/lib/51degrees/device.dat"
                51degrees-property-name-list: "IsMobile,PlatformName,PlatformVersion"
                51degrees-property-separator: "|"
                51degrees-cache-size: 5000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_data_file == "/var/lib/51degrees/device.dat"
        assert ir.global_config.fiftyone_degrees_property_name_list == "IsMobile,PlatformName,PlatformVersion"
        assert ir.global_config.fiftyone_degrees_property_separator == "|"
        assert ir.global_config.fiftyone_degrees_cache_size == 5000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-data-file /var/lib/51degrees/device.dat" in output
        assert "51degrees-property-name-list IsMobile,PlatformName,PlatformVersion" in output
        assert "51degrees-property-separator |" in output
        assert "51degrees-cache-size 5000" in output


class TestPhase9WURFL:
    """Test WURFL device detection directives."""

    def test_wurfl_data_file(self):
        """Test wurfl-data-file directive."""
        config = """
        config test {
            global {
                wurfl-data-file: "/etc/haproxy/wurfl.xml"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_data_file == "/etc/haproxy/wurfl.xml"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-data-file /etc/haproxy/wurfl.xml" in output

    def test_wurfl_information_list(self):
        """Test wurfl-information-list directive."""
        config = """
        config test {
            global {
                wurfl-information-list: "model_name,brand_name,is_smartphone"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_information_list == "model_name,brand_name,is_smartphone"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-information-list model_name,brand_name,is_smartphone" in output

    def test_wurfl_information_list_separator(self):
        """Test wurfl-information-list-separator directive."""
        config = """
        config test {
            global {
                wurfl-information-list-separator: ","
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_information_list_separator == ","

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-information-list-separator ," in output

    def test_wurfl_patch_file(self):
        """Test wurfl-patch-file directive."""
        config = """
        config test {
            global {
                wurfl-patch-file: "/etc/haproxy/wurfl-patch.xml"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_patch_file == "/etc/haproxy/wurfl-patch.xml"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-patch-file /etc/haproxy/wurfl-patch.xml" in output

    def test_wurfl_cache_size(self):
        """Test wurfl-cache-size directive."""
        config = """
        config test {
            global {
                wurfl-cache-size: 100000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_cache_size == 100000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-cache-size 100000" in output

    def test_wurfl_engine_mode(self):
        """Test wurfl-engine-mode directive."""
        config = """
        config test {
            global {
                wurfl-engine-mode: "performance"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_engine_mode == "performance"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-engine-mode performance" in output

    def test_wurfl_useragent_priority(self):
        """Test wurfl-useragent-priority directive."""
        config = """
        config test {
            global {
                wurfl-useragent-priority: "high_performance"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_useragent_priority == "high_performance"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-useragent-priority high_performance" in output

    def test_wurfl_complete_configuration(self):
        """Test complete WURFL configuration."""
        config = """
        config test {
            global {
                wurfl-data-file: "/var/lib/wurfl/wurfl.xml"
                wurfl-information-list: "is_tablet,is_smartphone,form_factor"
                wurfl-information-list-separator: "|"
                wurfl-patch-file: "/var/lib/wurfl/patch.xml"
                wurfl-cache-size: 80000
                wurfl-engine-mode: "accuracy"
                wurfl-useragent-priority: "override_sideloaded_browser_useragent"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.wurfl_data_file == "/var/lib/wurfl/wurfl.xml"
        assert ir.global_config.wurfl_information_list == "is_tablet,is_smartphone,form_factor"
        assert ir.global_config.wurfl_information_list_separator == "|"
        assert ir.global_config.wurfl_patch_file == "/var/lib/wurfl/patch.xml"
        assert ir.global_config.wurfl_cache_size == 80000
        assert ir.global_config.wurfl_engine_mode == "accuracy"
        assert ir.global_config.wurfl_useragent_priority == "override_sideloaded_browser_useragent"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "wurfl-data-file /var/lib/wurfl/wurfl.xml" in output
        assert "wurfl-information-list is_tablet,is_smartphone,form_factor" in output
        assert "wurfl-information-list-separator |" in output
        assert "wurfl-patch-file /var/lib/wurfl/patch.xml" in output
        assert "wurfl-cache-size 80000" in output
        assert "wurfl-engine-mode accuracy" in output
        assert "wurfl-useragent-priority override_sideloaded_browser_useragent" in output


class TestPhase9Integration:
    """Test integration of all device detection libraries."""

    def test_all_device_detection_libraries(self):
        """Test using all three device detection libraries together."""
        config = """
        config test {
            global {
                deviceatlas-json-file: "/etc/deviceatlas.json"
                deviceatlas-log-level: 1
                51degrees-data-file: "/etc/51degrees.dat"
                51degrees-cache-size: 10000
                wurfl-data-file: "/etc/wurfl.xml"
                wurfl-cache-size: 50000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.deviceatlas_json_file == "/etc/deviceatlas.json"
        assert ir.global_config.deviceatlas_log_level == 1
        assert ir.global_config.fiftyone_degrees_data_file == "/etc/51degrees.dat"
        assert ir.global_config.fiftyone_degrees_cache_size == 10000
        assert ir.global_config.wurfl_data_file == "/etc/wurfl.xml"
        assert ir.global_config.wurfl_cache_size == 50000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "deviceatlas-json-file /etc/deviceatlas.json" in output
        assert "deviceatlas-log-level 1" in output
        assert "51degrees-data-file /etc/51degrees.dat" in output
        assert "51degrees-cache-size 10000" in output
        assert "wurfl-data-file /etc/wurfl.xml" in output
        assert "wurfl-cache-size 50000" in output

    def test_device_detection_with_performance_tuning(self):
        """Test device detection with performance tuning directives."""
        config = """
        config test {
            global {
                tune.bufsize: 16384
                deviceatlas-json-file: "/etc/deviceatlas.json"
                tune.maxaccept: 64
                wurfl-data-file: "/etc/wurfl.xml"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.bufsize") == 16384
        assert ir.global_config.deviceatlas_json_file == "/etc/deviceatlas.json"
        assert ir.global_config.tuning.get("tune.maxaccept") == 64
        assert ir.global_config.wurfl_data_file == "/etc/wurfl.xml"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.bufsize 16384" in output
        assert "deviceatlas-json-file /etc/deviceatlas.json" in output
        assert "tune.maxaccept 64" in output
        assert "wurfl-data-file /etc/wurfl.xml" in output
