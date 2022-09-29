# Databricks notebook source
# DBTITLE 1,Notebook Description
# MAGIC %md
# MAGIC The following notebook:
# MAGIC   1. Reads the Noblehire.io Raw data;
# MAGIC      - It contains about four hundred columns, some of which contains nested json objects. Also, it covers different topics;
# MAGIC   2. Cleans and transforms the data;
# MAGIC      - The nested columns are being unpacked and the total columns number goes above one hundred thousand;
# MAGIC   3. Creates thirteen separate DataFrames out of the Raw dataset.
# MAGIC      - Because of the huge amount of columns and due to the data covering different topics, it is splited. 
# MAGIC      
# MAGIC The output of this notebook are the following DataFrames (also saved as .csv files in ADLS)
# MAGIC   - Company Locations Address;
# MAGIC   - Company Locations;
# MAGIC   - Company General;
# MAGIC   - Company Awards;
# MAGIC   - Company Perks;
# MAGIC   - Company Values;
# MAGIC   - Job Requirements;
# MAGIC   - Job Benefits;
# MAGIC   - Job Responsibilities;
# MAGIC   - Job Tools;
# MAGIC   - Job Activities;
# MAGIC   - Job Hiring Process;
# MAGIC   - Posts General.
# MAGIC   
# MAGIC All datasets can be joined together via the post_id or company_id columns.

# COMMAND ----------

# DBTITLE 1,Imports
from datetime import date
import time
import pandas as pd
import numpy as np
from flatten_json import flatten
from pyspark.sql.types import *
from pyspark.sql.functions import *

# COMMAND ----------

# DBTITLE 1,Define variables
# Date variables 
current_year = date.today().year
current_month = "0" + str(date.today().month) if len(str(date.today().month)) == 1 else date.today().month
current_day = "0" + str(date.today().day) if len(str(date.today().day)) == 1 else date.today().day

# Base location variables
location_prefix = "/dbfs"
main_path = "/mnt/adlslirkov/it-job-boards/Noblehire.io/base/"
company_locations_address_path = f"companyLocationsAddress/{current_year}/{current_month}/{current_day}/"
company_general_path = f"companyGeneral/{current_year}/{current_month}/{current_day}/"
company_awards_path = f"companyAwards/{current_year}/{current_month}/{current_day}/"
company_perks_path = f"companyPerks/{current_year}/{current_month}/{current_day}/"
company_values_path = f"companyValues/{current_year}/{current_month}/{current_day}/"
company_locations_path = f"companyLocations/{current_year}/{current_month}/{current_day}/"
job_requirements_path = f"jobRequirements/{current_year}/{current_month}/{current_day}/"
job_benefits_path = f"jobBenefits/{current_year}/{current_month}/{current_day}/"
job_responsibilities_path = f"jobResponsibilities/{current_year}/{current_month}/{current_day}/"
job_tools_path = f"jobTools/{current_year}/{current_month}/{current_day}/"
job_activities_path = f"jobActivities/{current_year}/{current_month}/{current_day}/"
job_hiring_process_path = f"jobHiringProcess/{current_year}/{current_month}/{current_day}/"
posts_path = f"posts/{current_year}/{current_month}/{current_day}/"

# COMMAND ----------

# DBTITLE 1,Define functions
# Define a function to flatten complex nested struct type columns
def flatten_struct_df(nested_df):
    flat_cols = [c[0] for c in nested_df.dtypes if c[1][:6] != 'struct']
    nested_cols = [c[0] for c in nested_df.dtypes if c[1][:6] == 'struct']

    flat_df = nested_df.select(flat_cols +
                               [col(nc+'.'+c).alias(nc+'_'+c)
                                for nc in nested_cols
                                for c in nested_df.select(nc+'.*').columns])
    return nested_df


# Define a function to flatten complex nested struct and array type columns
def flatten(df):
  # compute Complex Fields (Lists and Structs) in Schema   
  complex_fields = dict([(field.name, field.dataType) for field in df.schema.fields if type(field.dataType) == ArrayType or type(field.dataType) == StructType])
  
  while len(complex_fields)!=0:
    col_name=list(complex_fields.keys())[0]
    print ("Processing :"+col_name+" Type : "+str(type(complex_fields[col_name])))
    
    # if StructType then convert all sub elements to columns.
    # i.e. flatten structs
    if (type(complex_fields[col_name]) == StructType):
      expanded = [col(col_name+'.'+k).alias(col_name+'_'+k) for k in [ n.name for n in  complex_fields[col_name]]]
      df=df.select("*", *expanded).drop(col_name)
      
    # if ArrayType then add the Array Elements as Rows using the explode_outer function
    # i.e. explode Arrays
    elif (type(complex_fields[col_name]) == ArrayType):    
      df=df.withColumn(col_name,explode_outer(col_name))
    
    complex_fields = dict([(field.name, field.dataType) for field in df.schema.fields if type(field.dataType) == ArrayType or  type(field.dataType) == StructType])
  return df

# COMMAND ----------

# DBTITLE 1,Read Raw data
df = spark.read.format("json").load("/mnt/adlslirkov/it-job-boards/testing/JSON/*.json")

df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Activities

# COMMAND ----------

# DBTITLE 1,Activities
# Dynamically unpack columns with Struct or Array data type

# Get the number of columns to unpack
activities_max_size = df.select(max(size(col("activities")))).collect()

results={}
for i in activities_max_size:
  results.update(i.asDict())

df_activities = df.select(col("id"), *[col("activities")[i] for i in range(results["max(size(activities))"])])

# Drop the column from the Raw DataFrame
df = df.drop("activities")

df_activities = flatten(df_activities)


# Rename columns
for column in df_activities.columns:
    new_column = column.replace("[", "_").replace("]", "")
    df_activities = df_activities.withColumnRenamed(column, new_column)
    

df_activities.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Benefits

# COMMAND ----------

# DBTITLE 1,Benefits
# Dynamically unpack columns with Struct or Array data type

# Get the number of columns to unpack
benefits_max_size = df.select(max(size(col("benefits")))).collect()

results={}
for i in benefits_max_size:
  results.update(i.asDict())

df_benefits = df.select(col("id"), *[col("benefits")[i] for i in range(results["max(size(benefits))"])])

# Drop the column from the Raw DataFrame
df = df.drop("benefits")

df_benefits = flatten(df_benefits)


# Rename columns
for column in df_benefits.columns:
    new_column = column.replace("[", "_").replace("]", "")
    df_benefits = df_benefits.withColumnRenamed(column, new_column)
    

df_benefits.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Company

# COMMAND ----------

df_companies = df.select("company").distinct()


df_companies = (df_companies
  .select(
      col("company.brand"), 
      col("company.id"), 
      col("company.overview"), 
      col("company.product"), 
      col("company.public"), 
      col("company.slug"), 
      col("company.awards.icon").alias("company_awards_icon"), 
      col("company.awards.title").alias("company_awards_title"), 
      col("company.images.collection").alias("company_images_collection"), 
      col("company.images.id").alias("company_images_id"), 
      col("company.images.name").alias("company_images_name"), 
      col("company.locations.address").alias("company_locations_address"), 
      col("company.locations.comment").alias("company_locations_comment"), 
      col("company.locations.founded").alias("company_locations_founded"), 
      col("company.locations.id").alias("company_locations_id"), 
      col("company.locations.teamSize").alias("company_locations_teamSize"), 
      col("company.perks.icon").alias("company_perks_icon"), 
      col("company.perks.text").alias("company_perks_text"), 
      col("company.perks.title").alias("company_perks_title"), 
      col("company.values.icon").alias("company_values_icon"), 
      col("company.values.text").alias("company_values_text"), 
      col("company.values.title").alias("company_values_title")
  )
)


df_companies = (df_companies
  .select(
      "*",
      *[col("company_awards_icon")[i] for i in range(df_companies.select(max(size(col("company_awards_icon"))).alias("max_size")).first()["max_size"])],
      *[col("company_awards_title")[i] for i in range(df_companies.select(max(size(col("company_awards_title"))).alias("max_size")).first()["max_size"])],
      *[col("company_images_collection")[i] for i in range(df_companies.select(max(size(col("company_images_collection"))).alias("max_size")).first()["max_size"])],
      *[col("company_images_id")[i] for i in range(df_companies.select(max(size(col("company_images_id"))).alias("max_size")).first()["max_size"])],
      *[col("company_images_name")[i] for i in range(df_companies.select(max(size(col("company_images_name"))).alias("max_size")).first()["max_size"])],
      *[col("company_locations_address")[i] for i in range(df_companies.select(max(size(col("company_locations_address"))).alias("max_size")).first()["max_size"])],
      *[col("company_locations_comment")[i] for i in range(df_companies.select(max(size(col("company_locations_comment"))).alias("max_size")).first()["max_size"])],
      *[col("company_locations_founded")[i] for i in range(df_companies.select(max(size(col("company_locations_founded"))).alias("max_size")).first()["max_size"])],
      *[col("company_locations_id")[i] for i in range(df_companies.select(max(size(col("company_locations_id"))).alias("max_size")).first()["max_size"])],
      *[col("company_locations_teamSize")[i] for i in range(df_companies.select(max(size(col("company_locations_teamSize"))).alias("max_size")).first()["max_size"])],
      *[col("company_perks_icon")[i] for i in range(df_companies.select(max(size(col("company_perks_icon"))).alias("max_size")).first()["max_size"])],
      *[col("company_perks_text")[i] for i in range(df_companies.select(max(size(col("company_perks_text"))).alias("max_size")).first()["max_size"])],
      *[col("company_perks_title")[i] for i in range(df_companies.select(max(size(col("company_perks_title"))).alias("max_size")).first()["max_size"])],
      *[col("company_values_icon")[i] for i in range(df_companies.select(max(size(col("company_values_icon"))).alias("max_size")).first()["max_size"])],
      *[col("company_values_text")[i] for i in range(df_companies.select(max(size(col("company_values_text"))).alias("max_size")).first()["max_size"])],
      *[col("company_values_title")[i] for i in range(df_companies.select(max(size(col("company_values_title"))).alias("max_size")).first()["max_size"])]
  )
).drop(
    "company_awards_icon",
    "company_awards_title",
    "company_images_collection",
    "company_images_id",
    "company_images_name",
    "company_locations_address",
    "company_locations_comment",
    "company_locations_founded",
    "company_locations_id",
    "company_locations_teamSize",
    "company_perks_icon",
    "company_perks_text", 
    "company_perks_title",
    "company_values_icon",
    "company_values_text",
    "company_values_title"
)


df_companies.display()

# COMMAND ----------

# Dynamically unpack the location columns. 
# These columns contain information about the various companies' office locations. 
# The number of these columns might vary, so they need to be dynamicallt unpacked. 
# This is implemented using a script that executes in a loop for each location_address column.

for column in df_companies.columns:
    if "company_locations_address" in column:
        
        df_companies_clean = (df_companies
         # Take location_<n>_address column
         .select(
             "id", 
             column
         )
         # locations_<n>_address
         .select(
             "*", 
             json_tuple(
                 column, 
                 "address_components", 
                 "formatted_address", 
                 "geometry", 
                 "place_id", 
                 "types"
             ).alias(
                 f"{column + '_'}address_components", 
                 f"{column + '_'}formatted_address", 
                 f"{column + '_'}geometry", 
                 f"{column + '_'}place_id", 
                 f"{column + '_'}types"
             )
         ).drop(column) 
         # geometry
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}geometry", 
                 "bounds", 
                 "location", 
                 "location_type", 
                 "viewport"
             ).alias(
                 f"{column + '_'}bounds", 
                 f"{column + '_'}location", 
                 f"{column + '_'}location_type", 
                 f"{column + '_'}viewport"
             )
         ).drop(column + "_" + f"geometry")
         # location
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}location", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}latitude", 
                 f"{column + '_'}longitude")
         ).drop(column + "_" + "location")
         # viewport
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}viewport", 
                 "northeast", 
                 "southwest"
             ).alias(
                 f"{column + '_'}viewport_northeast", 
                 f"{column + '_'}viewport_southwest"
             )
         ).drop(column + "_" + "viewport")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}viewport_northeast", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}viewport_northeast_latitude", 
                 f"{column + '_'}viewport_northeast_longitude"
             )
         ).drop(column + "_" + "viewport_northeast")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}viewport_southwest", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}viewport_southwest_latitude", 
                 f"{column + '_'}viewport_southwest_longitude")
         ).drop(column + "_" + "viewport_southwest")
         # bounds
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}bounds", 
                 "northeast", 
                 "southwest"
             ).alias(
                 f"{column + '_'}bounds_northeast", 
                 f"{column + '_'}bounds_southwest"
             )
         ).drop(column + "_" + "bounds")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}bounds_northeast", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}bounds_northeast_latitude", 
                 f"{column + '_'}bounds_northeast_longitude"
             )
         ).drop(column + "_" + "bounds_northeast")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}bounds_southwest", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}bounds_southwest_latitude", 
                 f"{column + '_'}bounds_southwest_longitude"
             )
         ).drop(column + "_" + "bounds_southwest")
#          # types
#          .selectExpr(
#              "*", 
#              f"from_json({column + '_'}types, 'array<string>') as {column + '_'}types_array"
#          ).drop(f"{column + '_'}types")
        )

#         #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
#         df_companies_clean = (df_companies_clean
#          # types - continuation
#          .select(
#              "*", 
#              *[col(f"{column + '_'}types_array")[i] for i in range(df_companies_clean.select(max(size(col(f"{column + '_'}types_array"))).alias("max_size")).first()["max_size"])]
#          ).drop(f"{column + '_'}types_array")
#         )
        
#         #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#         # address_components
#         df_companies_clean = df_companies_clean.selectExpr(
#             "*", 
#             f"from_json({column + '_'}address_components, 'array<struct<long_name:string,short_name:string,types:array<string>>>') as {column + '_'}address_components_array"
#         ).drop(f"{column + '_'}address_components")
        
#         #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#         # address_components - continuation
#         df_companies_clean = df_companies_clean.select(
#             "*", 
#             *[col(f"{column + '_'}address_components_array")[i] for i in range(df_companies_clean.select(max(size(col(f"{column + '_'}address_components_array"))).alias("max_size")).first()["max_size"])]
#         ).drop(f"{column + '_'}address_components_array")
        
#         #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#         # address_components - continuation
#         df_companies_clean = df_companies_clean.select(
#             "*", 
#             *[col(c).long_name for c in df_companies_clean.columns if "address_components_array" in c], *[col(c).short_name for c in df_companies_clean.columns if "address_components_array" in c], *[col(c).types for c in df_companies_clean.columns if "address_components_array" in c]
#         ).drop(
#             *[c for c in df_companies_clean.columns if c.startswith(f"{column + '_'}address_components_array[") == True and c.endswith("]") == True]
#         )
        
#         #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#         # rename columns to remove any dots in column names caused by the selection of nested objects
#         df_companies_clean = df_companies_clean.toDF(*(c.replace('.', '_') for c in df_companies_clean.columns))
        
#         #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#         # address_components types
#         df_companies_clean = df_companies_clean.select(
#             "*", 
#             *[col(c)[i] for c in df_companies_clean.columns if c.endswith(f"types") == True for i in range(df_companies_clean.select(max(size(col(c))).alias(str(c) + "_max_size")).first()[str(c) + "_max_size"])]
#         ).drop(
#             *[c for c in df_companies_clean.columns if c.endswith("types") == True]
#         )
        
#         #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
#         # join clean DataFrame back to the original DataFrame and drop the unpacked column
#         df_companies = df_companies.join(df_companies_clean, ["id"], how="inner").drop(column)
        df_companies_clean.display()

    
df_companies.display()

# COMMAND ----------

# DBTITLE 1,Company
# df_companies = (df_companies
#   # company_locations_address
#   .select(
#       "*", 
#       json_tuple(
#           "company_locations_address", 
#           "address_components", 
#           "formatted_address", 
#           "geometry", 
#           "place_id", 
#           "types"
#       ).alias(
#           "address_components", 
#           "formatted_address", 
#           "geometry", 
#           "place_id", 
#           "types")
#   ).drop("company_locations_address")
#  # geometry
#  .select(
#      "*", 
#      json_tuple(
#          "geometry", 
#          "bounds", 
#          "location", 
#          "location_type", 
#          "viewport"
#      ).alias(
#          "bounds", 
#          "location", 
#          "location_type", 
#          "viewport")
#  ).drop("geometry")
#  # location
#  .select(
#      "*", 
#      json_tuple(
#          "location", 
#          "lat", 
#          "lng"
#      ).alias(
#          "latitude", 
#          "longitude"
#      )
#  ).drop("location")
#  # viewport
#  .select(
#      "*", 
#      json_tuple(
#          "viewport", 
#          "northeast", 
#          "southwest"
#      ).alias(
#          "viewport_northeast", 
#          "viewport_southwest"
#      )
#  ).drop("viewport")
#  .select(
#      "*", 
#      json_tuple(
#          "viewport_northeast", 
#          "lat", 
#          "lng"
#      ).alias(
#          "viewport_northeast_latitude", 
#          "viewport_northeast_longitude"
#      )
#  ).drop("viewport_northeast")
#  .select(
#      "*", 
#      json_tuple(
#          "viewport_southwest", 
#          "lat", 
#          "lng"
#      ).alias(
#          "viewport_southwest_latitude", 
#          "viewport_southwest_longitude"
#      )
#  ).drop("viewport_southwest")
#  bounds
#  .select(
#      "*", 
#      json_tuple(
#          "bounds", 
#          "northeast", 
#          "southwest"
#      ).alias(
#          "bounds_northeast", 
#          "bounds_southwest"
#      )
#  ).drop("bounds")
#  .select(
#      "*", 
#      json_tuple(
#          "bounds_northeast", 
#          "lat", 
#          "lng"
#      ).alias(
#          "bounds_northeast_latitude", 
#          "bounds_northeast_longitude"
#      )
#  ).drop("bounds_northeast")
#  .select(
#      "*", 
#      json_tuple(
#          "bounds_southwest", 
#          "lat", 
#          "lng"
#      ).alias(
#          "bounds_southwest_latitude", 
#          "bounds_southwest_longitude"
#      )
#  ).drop("bounds_southwest")
# types - can be removed
#  .selectExpr(
#      "*", 
#      "from_json(types, 'array<string>') as types_array"
#  ).drop("types")
# )


# df_companies = (df_companies
#  # types - continuation
#  .select(
#      "*", 
#      *[col("types_array")[i] for i in range(df_companies.select(max(size(col("types_array"))).alias("max_size")).first()["max_size"])]
#  ).drop("types_array")
# )


# df_companies = df_companies.selectExpr(
#     "*", 
#     "from_json(address_components, 'array<struct<long_name:string,short_name:string,types:array<string>>>') as address_components_array"
# ).drop("address_components")

# df_companies = df_companies.select(
#     "*", 
#     *[col("address_components_array")[i] for i in range(df_companies.select(max(size(col("address_components_array"))).alias("max_size")).first()["max_size"])]
# ).drop("address_components_array")


# df_companies = df_companies.select(
#     "*", 
#     *[col(column).long_name for column in df_companies.columns if "address_components_array" in column], *[col(column).short_name for column in df_companies.columns if "address_components_array" in column], *[col(column).types for column in df_companies.columns if "address_components_array" in column]
# ).drop(
#     *[column for column in df_companies.columns if column.startswith("address_components_array[") == True and column.endswith("]") == True]
# )


# df_companies = df_companies.toDF(*(column.replace('.', '_') for column in df_companies.columns))


# df_companies = df_companies.select(
#     "*", 
#     *[col(column)[i] for column in df_companies.columns if column.endswith("types") == True for i in range(df_companies.select(max(size(col(column))).alias(str(column) + "_max_size")).first()~[str(column) + "_max_size"])]
# ).drop(
#     *[column for column in df_companies.columns if column.endswith("types") == True]
# )


# df_companies.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Hiring Process Steps

# COMMAND ----------

# DBTITLE 1,hiringProcessSteps
# Dynamically unpack columns with Struct or Array data type

# Get the number of columns to unpack
hiringprocesssteps_max_size = df.select(max(size(col("hiringProcessSteps")))).collect()

results={}
for i in hiringprocesssteps_max_size:
  results.update(i.asDict())

df_hiringprocesssteps = df.select(col("id"), *[col("hiringProcessSteps")[i] for i in range(results["max(size(hiringProcessSteps))"])])

# Drop the column from the Raw DataFrame
df = df.drop("hiringProcessSteps")


# Rename columns
for column in df_hiringprocesssteps.columns:
    new_column = column.replace("[", "_").replace("]", "")
    df_hiringprocesssteps = df_hiringprocesssteps.withColumnRenamed(column, new_column)
    

df_hiringprocesssteps.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Locations

# COMMAND ----------

# DBTITLE 1,Locations
# Dynamically unpack columns with Struct or Array data type

# Get the number of columns to unpack
locations_max_size = df.select(max(size(col("locations")))).collect()

results={}
for i in locations_max_size:
  results.update(i.asDict())

df_locations = df.select(col("id"), *[col("locations")[i] for i in range(results["max(size(locations))"])])

# Drop the column from the Raw DataFrame
df = df.drop("locations")

df_locations = flatten(df_locations)


# Rename columns
for column in df_locations.columns:
    new_column = column.replace("[", "_").replace("]", "")
    df_locations = df_locations.withColumnRenamed(column, new_column)
    

df_locations.display()

# COMMAND ----------

# DBTITLE 1,Locations
# Dynamically unpack the location columns. 
# These columns contain information about the various companies' office locations. 
# The number of these columns might vary, so they need to be dynamicallt unpacked. 
# This is implemented using a script that executes in a loop for each location_address column.

for column in df_locations.columns:
    if column.endswith("address") == True:
        
        df_locations_clean = (df_locations
         # Take location_<n>_address column
         .select(
             "id", 
             column
         )
         # locations_<n>_address
         .select(
             "*", 
             json_tuple(
                 column, 
                 "address_components", 
                 "formatted_address", 
                 "geometry", 
                 "place_id", 
                 "types"
             ).alias(
                 f"{column + '_'}address_components", 
                 f"{column + '_'}formatted_address", 
                 f"{column + '_'}geometry", 
                 f"{column + '_'}place_id", 
                 f"{column + '_'}types"
             )
         ).drop(column) 
         # geometry
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}geometry", 
                 "bounds", 
                 "location", 
                 "location_type", 
                 "viewport"
             ).alias(
                 f"{column + '_'}bounds", 
                 f"{column + '_'}location", 
                 f"{column + '_'}location_type", 
                 f"{column + '_'}viewport"
             )
         ).drop(column + "_" + f"geometry")
         # location
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}location", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}latitude", 
                 f"{column + '_'}longitude")
         ).drop(column + "_" + "location")
         # viewport
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}viewport", 
                 "northeast", 
                 "southwest"
             ).alias(
                 f"{column + '_'}viewport_northeast", 
                 f"{column + '_'}viewport_southwest"
             )
         ).drop(column + "_" + "viewport")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}viewport_northeast", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}viewport_northeast_latitude", 
                 f"{column + '_'}viewport_northeast_longitude"
             )
         ).drop(column + "_" + "viewport_northeast")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}viewport_southwest", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}viewport_southwest_latitude", 
                 f"{column + '_'}viewport_southwest_longitude")
         ).drop(column + "_" + "viewport_southwest")
         # bounds
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}bounds", 
                 "northeast", 
                 "southwest"
             ).alias(
                 f"{column + '_'}bounds_northeast", 
                 f"{column + '_'}bounds_southwest"
             )
         ).drop(column + "_" + "bounds")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}bounds_northeast", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}bounds_northeast_latitude", 
                 f"{column + '_'}bounds_northeast_longitude"
             )
         ).drop(column + "_" + "bounds_northeast")
         .select(
             "*", 
             json_tuple(
                 f"{column + '_'}bounds_southwest", 
                 "lat", 
                 "lng"
             ).alias(
                 f"{column + '_'}bounds_southwest_latitude", 
                 f"{column + '_'}bounds_southwest_longitude"
             )
         ).drop(column + "_" + "bounds_southwest")
         # types
         .selectExpr(
             "*", 
             f"from_json({column + '_'}types, 'array<string>') as {column + '_'}types_array"
         ).drop(f"{column + '_'}types")
        )

        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        df_locations_clean = (df_locations_clean
         # types - continuation
         .select(
             "*", 
             *[col(f"{column + '_'}types_array")[i] for i in range(df_locations_clean.select(max(size(col(f"{column + '_'}types_array"))).alias("max_size")).first()["max_size"])]
         ).drop(f"{column + '_'}types_array")
        )
        
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # address_components
        df_locations_clean = df_locations_clean.selectExpr(
            "*", 
            f"from_json({column + '_'}address_components, 'array<struct<long_name:string,short_name:string,types:array<string>>>') as {column + '_'}address_components_array"
        ).drop(f"{column + '_'}address_components")
        
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # address_components - continuation
        df_locations_clean = df_locations_clean.select(
            "*", 
            *[col(f"{column + '_'}address_components_array")[i] for i in range(df_locations_clean.select(max(size(col(f"{column + '_'}address_components_array"))).alias("max_size")).first()                   ["max_size"])]
        ).drop(f"{column + '_'}address_components_array")
        
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # address_components - continuation
        df_locations_clean = df_locations_clean.select(
            "*", 
            *[col(c).long_name for c in df_locations_clean.columns if "address_components_array" in c], *[col(c).short_name for c in                                                                           df_locations_clean.columns if "address_components_array" in c], *[col(c).types for c in df_locations_clean.columns if "address_components_array" in c]
        ).drop(
            *[c for c in df_locations_clean.columns if c.startswith(f"{column + '_'}address_components_array[") == True and c.endswith("]") == True]
        )
        
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # rename columns to remove any dots in column names caused by the selection of nested objects
        df_locations_clean = df_locations_clean.toDF(*(c.replace('.', '_') for c in df_locations_clean.columns))
        
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        # address_components types
        df_locations_clean = df_locations_clean.select(
            "*", 
            *[col(c)[i] for c in df_locations_clean.columns if c.endswith(f"types") == True for i in range(df_locations_clean.select(max(size(col(c))).alias(str(c) +                                           "_max_size")).first()[str(c) + "_max_size"])]
        ).drop(
            *[c for c in df_locations_clean.columns if c.endswith("types") == True]
        )
        
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        # join clean DataFrame back to the original DataFrame and drop the unpacked column
        df_locations = df_locations.join(df_locations_clean, ["id"], how="inner").drop(column)
#         df_locations_clean.display()

    
df_locations.display()

# COMMAND ----------

# # Unpack the location columns

# df_locations = (df_locations
#  # Take locations 0
#  .select(
#      "id", 
#      "locations_0_address", 
#      "locations_0_comment", 
#      "locations_0_founded", 
#      "locations_0_id", 
#      "locations_0_teamSize"
#  )
#  # locations_0_address
#  .select(
#      "*", 
#      json_tuple(
#          "locations_0_address", 
#          "address_components", 
#          "formatted_address", 
#          "geometry", 
#          "place_id", 
#          "types"
#      ).alias(
#          "address_components", 
#          "formatted_address", 
#          "geometry", 
#          "place_id", 
#          "types"
#      )
#  ).drop("locations_0_address") 
#  # geometry
#  .select(
#      "*", 
#      json_tuple(
#          "geometry", 
#          "bounds", 
#          "location", 
#          "location_type", 
#          "viewport"
#      ).alias(
#          "bounds", 
#          "location", 
#          "location_type", 
#          "viewport"
#      )
#  ).drop("geometry")
#  # location
#  .select(
#      "*", 
#      json_tuple(
#          "location", 
#          "lat", 
#          "lng"
#      ).alias(
#          "latitude", 
#          "longitude")
#  ).drop("location")
#  # viewport
#  .select(
#      "*", 
#      json_tuple(
#          "viewport", 
#          "northeast", 
#          "southwest"
#      ).alias(
#          "viewport_northeast", 
#          "viewport_southwest"
#      )
#  ).drop("viewport")
#  .select(
#      "*", 
#      json_tuple(
#          "viewport_northeast", 
#          "lat", 
#          "lng"
#      ).alias(
#          "viewport_northeast_latitude", 
#          "viewport_northeast_longitude"
#      )
#  ).drop("viewport_northeast")
#  .select(
#      "*", 
#      json_tuple(
#          "viewport_southwest", 
#          "lat", 
#          "lng"
#      ).alias(
#          "viewport_southwest_latitude", "viewport_southwest_longitude")).drop("viewport_southwest")
#  # bounds
#  .select(
#      "*", 
#      json_tuple(
#          "bounds", 
#          "northeast", 
#          "southwest"
#      ).alias(
#          "bounds_northeast", 
#          "bounds_southwest"
#      )
#  ).drop("bounds")
#  .select(
#      "*", 
#      json_tuple(
#          "bounds_northeast", 
#          "lat", 
#          "lng"
#      ).alias(
#          "bounds_northeast_latitude", 
#          "bounds_northeast_longitude"
#      )
#  ).drop("bounds_northeast")
#  .select(
#      "*", 
#      json_tuple(
#          "bounds_southwest", 
#          "lat", 
#          "lng"
#      ).alias(
#          "bounds_southwest_latitude", 
#          "bounds_southwest_longitude"
#      )
#  ).drop("bounds_southwest")
#  # types
#  .selectExpr(
#      "*", 
#      "from_json(types, 'array<string>') as types_array"
#  ).drop("types")
# )
 
    
# df_locations = (df_locations
#  # types - continuation
#  .select(
#      "*", 
#      *[col("types_array")[i] for i in range(df_locations.select(max(size(col("types_array"))).alias("max_size")).first()["max_size"])]
#  ).drop("types_array")
# )


# df_locations = df_locations.selectExpr(
#     "*", 
#     "from_json(address_components, 'array<struct<long_name:string,short_name:string,types:array<string>>>') as address_components_array"
# ).drop("address_components")


# df_locations = df_locations.select(
#     "*", 
#     *[col("address_components_array")[i] for i in range(df_locations.select(max(size(col("address_components_array"))).alias("max_size")).first()["max_size"])]
# ).drop("address_components_array")


# df_locations = df_locations.select(
#     "*", 
#     *[col(column).long_name for column in df_locations.columns if "address_components_array" in column], *[col(column).short_name for column in df_locations.columns if "address_components_array"       in column], *[col(column).types for column in df_locations.columns if "address_components_array" in column]
# ).drop(
#     *[column for column in df_locations.columns if column.startswith("address_components_array[") == True and column.endswith("]") == True]
# )


# df_locations = df_locations.toDF(*(column.replace('.', '_') for column in df_locations.columns))


# df_locations = df_locations.select(
#     "*", 
#     *[col(column)[i] for column in df_locations.columns if column.endswith("types") == True for i in range(df_locations.select(max(size(col(column))).alias(str(column) + "_max_size")).first()         [str(column) + "_max_size"])]
# ).drop(
#     *[column for column in df_locations.columns if column.endswith("types") == True]
# )


# df_locations.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Requirements

# COMMAND ----------

# DBTITLE 1,Requirements
# Dynamically unpack columns with Struct or Array data type

# Get the number of columns to unpack
requirements_max_size = df.select(max(size(col("requirements")))).collect()

results={}
for i in requirements_max_size:
  results.update(i.asDict())

df_requirements = df.select(col("id"), *[col("requirements")[i] for i in range(results["max(size(requirements))"])])

# Drop the column from the Raw DataFrame
df = df.drop("requirements")

df_requirements = flatten(df_requirements)


# Rename columns
for column in df_requirements.columns:
    new_column = column.replace("[", "_").replace("]", "")
    df_requirements = df_requirements.withColumnRenamed(column, new_column)
    

df_requirements.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Responsibilities

# COMMAND ----------

# DBTITLE 1,Responsibilities
# Dynamically unpack columns with Struct or Array data type

# Get the number of columns to unpack
responsibilities_max_size = df.select(max(size(col("responsibilities")))).collect()

results={}
for i in responsibilities_max_size:
  results.update(i.asDict())

df_responsibilities = df.select(col("id"), *[col("responsibilities")[i] for i in range(results["max(size(responsibilities))"])])

# Drop the column from the Raw DataFrame
df = df.drop("responsibilities")

df_responsibilities = flatten(df_responsibilities)

# Rename columns
for column in df_responsibilities.columns:
    new_column = column.replace("[", "_").replace("]", "")
    df_responsibilities = df_responsibilities.withColumnRenamed(column, new_column)
    

df_responsibilities.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Tools

# COMMAND ----------

# DBTITLE 1,Tools
# Dynamically unpack columns with Struct or Array data type

# Get the number of columns to unpack
tools_max_size = df.select(max(size(col("tools")))).collect()

results={}
for i in tools_max_size:
  results.update(i.asDict())

df_tools = df.select(col("id"), *[col("tools")[i] for i in range(results["max(size(tools))"])])

df = df.drop("tools")


# Rename columns
for column in df_tools.columns:
    new_column = column.replace("[", "_").replace("]", "")
    df_tools = df_tools.withColumnRenamed(column, new_column)
    

df_tools.display()

# COMMAND ----------


