"""
Support for override functionality in script

Used for example to allow user to override what is written to `descriptor.mod` file or override regex search patterns
"""

from pathlib import Path

from methods.input_methods import parse_descriptor_to_dict


class OverrideClass:
    """Class to set up and support user overriding parameters/filenames/search patterns, etc."""

    def __init__(self, mod_github_folder_path: Path, debug_level: int = 0) -> None:
        """Fetch all user-specified overrides from a file `OVERRIDE.txt`"""
        # file for potential overrides
        # makes no sense to change name, filename MUST be this
        override_file_name = "OVERRIDE.txt"
        # file must be provided by user, must thus be with user's github repo
        override_file_path = mod_github_folder_path / override_file_name

        # if there are overrides, we parse them - use same structure as a paradox descriptor because we have the parser already
        self.overrides_enabled: bool = False
        """Class instance top-level setting, whether overrides were found"""

        self.override_dict: dict[str, str] = {}
        """Output dict from the overrides parsing, contains all current override values for this class instance"""

        if override_file_path.exists():
            self.overrides_enabled = True
            self.override_dict: dict[str, str] = parse_descriptor_to_dict(override_file_path, debug_level=debug_level)

        self.overriden_params: dict[str, bool] = {}
        """
        Book-keeping dict of parameter names and whether they were overriden or not.

        This will correspond to all overrides that were tried *outside* of the class by surrounding script.
        """

        if debug_level == "DEBUG":
            print("- Overrides: -")
            print(f"Override setting: {self.overrides_enabled}")
            if self.overrides_enabled:
                for key, item in self.override_dict.items():
                    print(f"{key}: {item}")
            else:
                print("No overrides")

    def get_parameter(self, parameter_name: str, parameter_default: str) -> str:
        """
        Check if parameter has an override and return, otherwise return specified fallback value

        skip entirely if no overrides
        """
        if not self.overrides_enabled:
            self.overriden_params[parameter_name] = False
            return parameter_default
        else:
            try:
                parameter = self.override_dict[f"{parameter_name}_override"]
                self.overriden_params[parameter_name] = True
            except KeyError:
                self.overriden_params[parameter_name] = False
                parameter = parameter_default

            return parameter
