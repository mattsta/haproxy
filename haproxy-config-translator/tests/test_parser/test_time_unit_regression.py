"""Regression tests for TIME_UNIT grammar fix.

This test suite ensures that TIME_UNIT tokens don't greedily match
across identifier boundaries, which was causing bugs like:
- "weight: 100\nmaxconn: 500" being parsed as "100m" (duration)
- "fall: 3\nssl: true" being parsed as "3s" (duration)
"""

import pytest

from haproxy_translator.parsers import DSLParser


class TestTimeUnitRegression:
    """Regression tests for TIME_UNIT word boundary fix."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_weight_before_maxconn(self, parser):
        """Test weight: 100 followed by maxconn doesn't parse as 100m duration."""
        source = """
        config test {
            template test {
                weight: 100
                maxconn: 500
            }
        }
        """
        ir = parser.parse(source)
        template = ir.templates["test"]

        # Should be integers, not duration strings
        assert template.parameters["weight"] == 100
        assert template.parameters["maxconn"] == 500
        assert isinstance(template.parameters["weight"], int)
        assert isinstance(template.parameters["maxconn"], int)

    def test_fall_before_ssl(self, parser):
        """Test fall: 3 followed by ssl doesn't parse as 3s duration."""
        source = """
        config test {
            template test {
                fall: 3
                ssl: true
            }
        }
        """
        ir = parser.parse(source)
        template = ir.templates["test"]

        # Should be int and bool, not duration strings
        assert template.parameters["fall"] == 3
        assert template.parameters["ssl"] is True
        assert isinstance(template.parameters["fall"], int)
        assert isinstance(template.parameters["ssl"], bool)

    def test_rise_before_maxconn(self, parser):
        """Test rise: 2 followed by maxconn doesn't parse as 2m duration."""
        source = """
        config test {
            template test {
                rise: 2
                maxconn: 100
            }
        }
        """
        ir = parser.parse(source)
        template = ir.templates["test"]

        assert template.parameters["rise"] == 2
        assert template.parameters["maxconn"] == 100
        assert isinstance(template.parameters["rise"], int)
        assert isinstance(template.parameters["maxconn"], int)

    def test_all_properties_with_potential_conflicts(self, parser):
        """Test all server properties that could trigger TIME_UNIT conflicts."""
        source = """
        config test {
            template full {
                check: true
                inter: 3s
                rise: 5
                fall: 2
                weight: 100
                maxconn: 500
                ssl: true
                verify: "none"
                backup: true
            }
        }
        """
        ir = parser.parse(source)
        template = ir.templates["full"]

        # Verify correct types
        assert template.parameters["check"] is True
        assert template.parameters["inter"] == "3s"  # Should be duration
        assert template.parameters["rise"] == 5
        assert template.parameters["fall"] == 2
        assert template.parameters["weight"] == 100  # NOT "100m"
        assert template.parameters["maxconn"] == 500  # NOT "500w" or similar
        assert template.parameters["ssl"] is True
        assert template.parameters["verify"] == "none"
        assert template.parameters["backup"] is True

        # Verify types are correct
        assert isinstance(template.parameters["weight"], int)
        assert isinstance(template.parameters["maxconn"], int)
        assert isinstance(template.parameters["rise"], int)
        assert isinstance(template.parameters["fall"], int)

    def test_durations_still_parse_correctly(self, parser):
        """Ensure actual durations still work after the word boundary fix."""
        source = """
        config test {
            defaults {
                timeout: {
                    connect: 5s
                    client: 100ms
                    server: 5m
                    check: 2h
                }
            }
        }
        """
        ir = parser.parse(source)
        defaults = ir.defaults

        # All should be duration strings
        assert defaults.timeout_connect == "5s"
        assert defaults.timeout_client == "100ms"
        assert defaults.timeout_server == "5m"
        assert defaults.timeout_check == "2h"

    def test_number_followed_by_identifier_starting_with_time_unit_letter(self, parser):
        """Test various numbers followed by identifiers starting with s, m, h, d."""
        test_cases = [
            ("weight: 100\nssl: true", {"weight": 100, "ssl": True}),
            ("rise: 2\nmaxconn: 100", {"rise": 2, "maxconn": 100}),
            ("fall: 3\nssl: false", {"fall": 3, "ssl": False}),
            ("maxconn: 500\nweight: 100", {"maxconn": 500, "weight": 100}),
        ]

        for properties, expected in test_cases:
            source = f"""
            config test {{
                template test {{
                    {properties}
                }}
            }}
            """
            ir = parser.parse(source)
            template = ir.templates["test"]

            for key, expected_value in expected.items():
                actual_value = template.parameters[key]
                assert actual_value == expected_value, (
                    f"{key}: expected {expected_value!r}, got {actual_value!r}"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
