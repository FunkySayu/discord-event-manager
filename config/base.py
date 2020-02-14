"""Base configuration holder."""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, TypeVar, Callable, Union

if TYPE_CHECKING:
    # Avoid cyclic imports used for typing only.
    from database.tables import ConfigsTable


T = TypeVar("T")


class ConfigVariable():
    """Wraps config property to implement lazy loading and automatic saving.

    This class is an implementation close to Python's property() function. It
    provides a user friendly interface for configuration function, documenting
    variables per configuration, providing default constructor, list of allowed
    values etc.

    Usage:
    >>> class MyConfig(Config):
    ...     my_variable = ConfigVariable(
    ...         key = "my_variable",             # Unique identifier
    ...         name = "My awesome variable",    # User friendly name
    ...         description = "Lots of things",  # Opt: documentation
    ...         values = ["foo", "bar"],         # Opt: allowed values
    ...         constructor = str,               # Opt: constructor
    ...         default = "foo")                 # Opt: default value.
    ...
    >>> config = MyConfig()
    >>> print(config.my_variable)
    foo
    >>> config.my_variable = "bar"
    >>> print(config.my_variable)
    bar

    :arg key: a unique identifier for this key, used to key the database
              entries. Ideally, you want to make it match the property's name
              used when declaring the configuration implementation.
    :arg name: a short, user friendly name, used to document the variable.
    :arg description: a long description, used for documentation.
    :arg values: optional list of possibly values. If specified, any other
                 values set to the variable will result in an exception.
    :arg constructor: optional constructor, used when accessing the variable.
    :arg default: optional default value for this property.
    """

    def __init__(self, *, key: str, name: str, description: str = "",
                 values: Optional[List[str]] = None,
                 constructor: Optional[Callable[[str], T]] = None,
                 default: Optional[str] = None):
        self.key = key
        self.name = name
        self.description = description
        self.values = values
        self.constructor = constructor
        self.default = default

    def __set__(self, config: BaseConfig, value: str):
        """Calls BaseConfig._set on the variable, saving it in the database."""
        if self.values is not None and value not in self.values:
            raise ValueError(
                f"Value '{value}' is not matching the allowed "
                f"values for '{self.key}'; expected one of"
                f"[{', '.join(self.values)}]")
        config._set(self.key, str(value))

    def __get__(self, config: BaseConfig, objtype=None) -> Union[T, str]:
        """Calls BaseConfig._get, retrieving it from the database."""
        constructor = self.constructor or str
        value = config._get(self.key) or self.default
        if value is None:
            raise KeyError(
                f"No value assigned for the key {self.key} and no default "
                "either.")
        return constructor(value)


class BaseConfig():
    """Base class providing tooling to manage configuration.

    Class inheriting this define configuration types (e.g. user config, server
    config...) with a set of variables. Each instance of this configuration
    represents the configuration for a specific entity (e.g. a specific user).

    Child classes must:
      - have a unique and defined CONFIGURATION_NAME, representing the table
        storing this configuration.
      - provide a unique ID for each entities they represent, representing a
        row in the table.

    Usage example:
    >>> class UserConfig(BaseConfig):
    ...     CONFIGURATION_NAME = "user"
    ...
    ...     prefered_meal = ConfigVariable(
    ...         key = "prefered_meal",
    ...         name = "Your prefered meal",
    ...         description = "Whatever you like, we can make it, so say it!",
    ...         values = ["pasta", "potatoes", "rice"],
    ...         default = "pasta")
    ...
    >>> table = ConfigsTable(Database())
    >>> foo_user = UserConfig(table, 111)
    >>> foo_user.prefered_meal = "rice"
    >>> bar_user = UserConfig(table, 222)
    >>> bar_user.prefered_meal = "potatoes"
    >>> print(foo_user.prefered_meal, bar_user.prefered_meal)
    rice, potatoes
    >>> # Make another instance, with the same idea as foo user.
    >>> another_instance_foo_user = UserConfig(table, 111)
    >>> print(anoterh_instance_foo_user.prefered_meal)
    rice

    :arg table: Database storing definition of the configurations.
    :arg id: a unique ID for the configuration of the entity.
    """

    CONFIGURATION_NAME = ""

    def __init__(self, table: ConfigsTable, id: str):
        if self.CONFIGURATION_NAME == "":
            raise NotImplementedError(
                "Configuration name was left undefined for this class.")
        self._table = table
        self.id = id

    def _set(self, key: str, value: str):
        """Stores a value in the database."""
        entry = self._table.get(self.CONFIGURATION_NAME, self.id)
        if entry is None:
            entry = {"id": self.id}

        entry[key] = value
        self._table.save(self.CONFIGURATION_NAME, entry)

    def _get(self, key: str) -> Optional[str]:
        """Gets the value of a configuration key."""
        entry = self._table.get(self.CONFIGURATION_NAME, self.id)
        if entry is None:
            return None
        return entry.get(key)
