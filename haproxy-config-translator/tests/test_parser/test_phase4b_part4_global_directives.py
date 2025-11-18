"""Tests for Phase 4B Part 4 global directives - Device Detection."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase4BPart4GlobalDirectives:
    """Test cases for Phase 4B Part 4 global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_deviceatlas_directives(self, parser, codegen):
        """Test DeviceAtlas device detection directives."""
        source = """
        config test {
            global {
                daemon: true
                deviceatlas-json-file: "/etc/haproxy/deviceatlas.json"
                deviceatlas-log-level: 3
                deviceatlas-separator: "|"
                deviceatlas-properties-cookie: "DAPROPS"
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.deviceatlas_json_file == "/etc/haproxy/deviceatlas.json"
        assert ir.global_config.deviceatlas_log_level == 3
        assert ir.global_config.deviceatlas_separator == "|"
        assert ir.global_config.deviceatlas_properties_cookie == "DAPROPS"

        assert "deviceatlas-json-file /etc/haproxy/deviceatlas.json" in output
        assert "deviceatlas-log-level 3" in output
        assert "deviceatlas-separator |" in output
        assert "deviceatlas-properties-cookie DAPROPS" in output

    def test_global_51degrees_directives(self, parser, codegen):
        """Test 51Degrees device detection directives."""
        source = """
        config test {
            global {
                daemon: true
                51degrees-data-file: "/etc/haproxy/51Degrees.dat"
                51degrees-property-name-list: "IsMobile,BrowserName"
                51degrees-property-separator: ","
                51degrees-cache-size: 10000
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.fiftyone_degrees_data_file == "/etc/haproxy/51Degrees.dat"
        assert ir.global_config.fiftyone_degrees_property_name_list == "IsMobile,BrowserName"
        assert ir.global_config.fiftyone_degrees_property_separator == ","
        assert ir.global_config.fiftyone_degrees_cache_size == 10000

        assert "51degrees-data-file /etc/haproxy/51Degrees.dat" in output
        assert "51degrees-property-name-list IsMobile,BrowserName" in output
        assert "51degrees-property-separator ," in output
        assert "51degrees-cache-size 10000" in output

    def test_global_wurfl_directives(self, parser, codegen):
        """Test WURFL device detection directives."""
        source = """
        config test {
            global {
                daemon: true
                wurfl-data-file: "/etc/haproxy/wurfl.xml"
                wurfl-information-list: "is_wireless_device,mobile_browser"
                wurfl-information-list-separator: ","
                wurfl-patch-file: "/etc/haproxy/wurfl_patch.xml"
                wurfl-cache-size: 100000
                wurfl-engine-mode: "accuracy"
                wurfl-useragent-priority: "plain"
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.wurfl_data_file == "/etc/haproxy/wurfl.xml"
        assert ir.global_config.wurfl_information_list == "is_wireless_device,mobile_browser"
        assert ir.global_config.wurfl_information_list_separator == ","
        assert ir.global_config.wurfl_patch_file == "/etc/haproxy/wurfl_patch.xml"
        assert ir.global_config.wurfl_cache_size == 100000
        assert ir.global_config.wurfl_engine_mode == "accuracy"
        assert ir.global_config.wurfl_useragent_priority == "plain"

        assert "wurfl-data-file /etc/haproxy/wurfl.xml" in output
        assert "wurfl-information-list is_wireless_device,mobile_browser" in output
        assert "wurfl-information-list-separator ," in output
        assert "wurfl-patch-file /etc/haproxy/wurfl_patch.xml" in output
        assert "wurfl-cache-size 100000" in output
        assert "wurfl-engine-mode accuracy" in output
        assert "wurfl-useragent-priority plain" in output

    def test_global_device_detection_mixed(self, parser, codegen):
        """Test multiple device detection systems together."""
        source = """
        config test {
            global {
                daemon: true

                // DeviceAtlas configuration
                deviceatlas-json-file: "/etc/haproxy/deviceatlas.json"
                deviceatlas-log-level: 2

                // 51Degrees configuration
                51degrees-data-file: "/etc/haproxy/51Degrees.dat"
                51degrees-cache-size: 5000
            }

            frontend web {
                bind *:443
                default_backend: web
            }

            backend web {
                servers {
                    server web1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify DeviceAtlas
        assert ir.global_config.deviceatlas_json_file == "/etc/haproxy/deviceatlas.json"
        assert ir.global_config.deviceatlas_log_level == 2

        # Verify 51Degrees
        assert ir.global_config.fiftyone_degrees_data_file == "/etc/haproxy/51Degrees.dat"
        assert ir.global_config.fiftyone_degrees_cache_size == 5000

        assert "deviceatlas-json-file /etc/haproxy/deviceatlas.json" in output
        assert "deviceatlas-log-level 2" in output
        assert "51degrees-data-file /etc/haproxy/51Degrees.dat" in output
        assert "51degrees-cache-size 5000" in output

    def test_global_phase4b_part4_comprehensive(self, parser, codegen):
        """Test all Phase 4B Part 4 directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000

                // DeviceAtlas Configuration
                deviceatlas-json-file: "/etc/haproxy/deviceatlas.json"
                deviceatlas-log-level: 1
                deviceatlas-separator: "|"
                deviceatlas-properties-cookie: "DA_PROPS"

                // 51Degrees Configuration
                51degrees-data-file: "/etc/haproxy/51Degrees.dat"
                51degrees-property-name-list: "IsMobile,DeviceType"
                51degrees-property-separator: ","
                51degrees-cache-size: 20000

                // WURFL Configuration
                wurfl-data-file: "/etc/haproxy/wurfl.xml"
                wurfl-information-list: "is_smartphone,brand_name"
                wurfl-information-list-separator: ":"
                wurfl-patch-file: "/etc/haproxy/custom_patch.xml"
                wurfl-cache-size: 50000
                wurfl-engine-mode: "performance"
                wurfl-useragent-priority: "useragent"
            }

            frontend api {
                bind *:443
                default_backend: api_backend
            }

            backend api_backend {
                servers {
                    server backend1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify all DeviceAtlas directives in IR
        assert ir.global_config.deviceatlas_json_file == "/etc/haproxy/deviceatlas.json"
        assert ir.global_config.deviceatlas_log_level == 1
        assert ir.global_config.deviceatlas_separator == "|"
        assert ir.global_config.deviceatlas_properties_cookie == "DA_PROPS"

        # Verify all 51Degrees directives in IR
        assert ir.global_config.fiftyone_degrees_data_file == "/etc/haproxy/51Degrees.dat"
        assert ir.global_config.fiftyone_degrees_property_name_list == "IsMobile,DeviceType"
        assert ir.global_config.fiftyone_degrees_property_separator == ","
        assert ir.global_config.fiftyone_degrees_cache_size == 20000

        # Verify all WURFL directives in IR
        assert ir.global_config.wurfl_data_file == "/etc/haproxy/wurfl.xml"
        assert ir.global_config.wurfl_information_list == "is_smartphone,brand_name"
        assert ir.global_config.wurfl_information_list_separator == ":"
        assert ir.global_config.wurfl_patch_file == "/etc/haproxy/custom_patch.xml"
        assert ir.global_config.wurfl_cache_size == 50000
        assert ir.global_config.wurfl_engine_mode == "performance"
        assert ir.global_config.wurfl_useragent_priority == "useragent"

        # Verify all directives in output
        assert "deviceatlas-json-file /etc/haproxy/deviceatlas.json" in output
        assert "deviceatlas-log-level 1" in output
        assert "deviceatlas-separator |" in output
        assert "deviceatlas-properties-cookie DA_PROPS" in output
        assert "51degrees-data-file /etc/haproxy/51Degrees.dat" in output
        assert "51degrees-property-name-list IsMobile,DeviceType" in output
        assert "51degrees-property-separator ," in output
        assert "51degrees-cache-size 20000" in output
        assert "wurfl-data-file /etc/haproxy/wurfl.xml" in output
        assert "wurfl-information-list is_smartphone,brand_name" in output
        assert "wurfl-information-list-separator :" in output
        assert "wurfl-patch-file /etc/haproxy/custom_patch.xml" in output
        assert "wurfl-cache-size 50000" in output
        assert "wurfl-engine-mode performance" in output
        assert "wurfl-useragent-priority useragent" in output
