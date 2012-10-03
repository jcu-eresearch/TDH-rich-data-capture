from sqlalchemy.dialects.mysql.base import VARCHAR, DOUBLE, INTEGER
from sqlalchemy.schema import ForeignKey

__author__ = 'Casey Bajema'

"""
    Base class for all calibration schemas that provide a known type.

    All calibration schemas that will be used need to be setup when creating the dataset.

    Each calibration schema has a 1:1 relationship with each data_entry.  This means that there can only
    be 1 QualitySchema calibration for a specific data_entry but there may be a different calibration
    (sub-classed from _CalibrationSchema) added to the same data_entry.
"""
class _CalibrationSchema():
    calibration_id = INTEGER()
    data_entry_id = ForeignKey("DataEntrySchema.data_entry_id")

"""
    Quality and calibration data about data_entry, there is a many to 1 relationship between quality
    and data_entry respectively.

    * Type and data_entry_id together form a unique key
    * Type is a short word describing what the quality information is
    * Unit of measure may not make sense for all quality data and is optional.
    * Description is an optional field for textual quality information that is out of the ordinary or cannot be
        represented as a number.
    * Value may be omitted for purely textual quality data
"""
class QualitySchema(_CalibrationSchema):
    unit = VARCHAR(50)              # (optional) Unit of measure
    description = VARCHAR(250)      # (Optional) Text based quality (eg. camera has a cracked lens) or further description of value
    value = DOUBLE()                # (Optional) A description

    #data_entry_id + type should be unique