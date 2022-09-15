# Databricks notebook source
from datetime import date
import time
import pandas as pd
import json
from flatten_json import flatten
from pyspark.sql.functions import *

# COMMAND ----------

# MAGIC %run "lirkov/IT Job Boards/Main"

# COMMAND ----------

# DBTITLE 1,Define variables
# Raw location variables
location_prefix = "/dbfs"
main_path = "/mnt/adlslirkov/it-job-boards/Noblehire.io/raw/"
posts_path = f"posts/{date.today().year}/{date.today().month}/{date.today().day}/"
posts_file_name = f"noblehireio-posts-{date.today()}.csv"

print(f"Posts path: {posts_path}; Posts file name: {posts_file_name}")

# COMMAND ----------

# DBTITLE 1,Scrape job posts
posts = scrape_Noblehire()

page = 0
flatten_posts_list = []
while len(posts.getPosts(page)) != 0:
    page += 1
    posts_response = posts.getPosts(page)
    for post in posts_response:
        flatten_posts_list.append(flatten(post))
    time.sleep(10)

# COMMAND ----------

# MAGIC %md
# MAGIC # Start of Testing Section

# COMMAND ----------

posts = scrape_Noblehire()

page = 0
while len(posts.getPosts(page)) != 0:
    page += 1
    posts_response = posts.getPosts(page)

    posts_response = json.dumps(posts_response)
    
    if len(posts_response) > 0:
        with open(f"/dbfs/mnt/adlslirkov/it-job-boards/testing/JSON/{page}.json", "w") as f:
            f.write(posts_response)
            f.close()
    
    time.sleep(10)

# COMMAND ----------

df = spark.read.format("json").load("/mnt/adlslirkov/it-job-boards/testing/JSON/2.json")

# df.select(explode_outer("activities").alias("activities"))

df.display()

# COMMAND ----------

df.printSchema()

# COMMAND ----------

tools_max_size = df.select(max(size(col("tools")))).collect()

results={}
for i in tools_max_size:
  results.update(i.asDict())

df_tools = df.select([col("tools")[i] for i in range(results["max(size(tools))"])])

df_tools.display()

# COMMAND ----------

tools_max_size = df.select(max(size(col("activities")))).collect()

results={}
for i in tools_max_size:
  results.update(i.asDict())

df_activities = df.select([col("activities")[i] for i in range(results["max(size(activities))"])])

# df_activities.dtypes

# df_activities.select(col("activities[0].timePercents").alias("activities_0_timePercents"), col("activities[0].title").alias("activities_0_tools")).display()

# cols = []
# for column in df_activities.columns:
#     cols.append(f"col('{column}').timePercents.alias('{column}_timePercents')")
#     cols.append(f"col('{column}').title.alias('{column}_title')")
    
df_activities.select("activities[0].timePercents").display()

# COMMAND ----------

activities[0]df_activitiesdf_activities.select(col('activities[0]').timePercents.alias('activities[0]_timePercents'), col('activities[0]').title.alias('activities[0]_title')).display()

# COMMAND ----------

df.select("activities.timePercents").display()

# COMMAND ----------

json_data = requests.get("https://prod-noblehire-api-000001.appspot.com/job?").json()
j = json.dumps(json_data)
with open("/dbfs/mnt/adlslirkov/it-job-boards/testing/page1.json", "w") as f:
    f.write(j)
    f.close()

# COMMAND ----------

data = requests.get("https://prod-noblehire-api-000001.appspot.com/job?").json()

import json
data = json.dumps(data)
# d = json.loads(data)
# print(type(d))

# COMMAND ----------

rddjson = sc.parallelize([data])
df = sqlContext.read.json(rddjson)

df.display()

# COMMAND ----------

posts = scrape_Noblehire()

page = 0
while len(posts.getPosts(page)) != 0:
    page += 1
    posts_response = posts.getPosts(page)

    posts_response = json.dumps(posts_response)
    
    rddjson = sc.parallelize([posts_response])
    df = sqlContext.read.json(rddjson)
    
    if df.count() > 0:
        df.write.option("overwrite", True).format("json").save(f"/mnt/adlslirkov/it-job-boards/testing/JSON/{page}")
    
    time.sleep(10)

# COMMAND ----------

dbutils.fs.rm("/mnt/adlslirkov/it-job-boards/testing/JSON/", True)

# COMMAND ----------

test = spark.read.format("json").load("/mnt/adlslirkov/it-job-boards/testing/JSON/7/")

# COMMAND ----------

rddjson = sc.parallelize([data])
df = sqlContext.read.json(rddjson)

df.display()

# COMMAND ----------

import json
jsonData = json.dumps(flatten_posts_list)

jsonDataList = []
jsonDataList.append(jsonData)

jsonRDD = sc.parallelize(jsonDataList)
df = spark.read.json(jsonRDD)
display(df)

# COMMAND ----------

df2 = df.select(col("id"),json_tuple(col("company_locations_0_address"),"address_components","formatted_address","geometry","place_id","types")) \
    .toDF("id","address_components","formatted_address","geometry","place_id","types")
df2.printSchema()

# COMMAND ----------

df2 = df2.select("id","address_components","formatted_address","place_id","types", json_tuple(col("geometry"), "bounds", "location", "location_type", "viewport")).toDF("id","address_components","formatted_address","place_id","types", "bounds", "location", "location_type", "viewport")

# COMMAND ----------

df2.display()

# COMMAND ----------

                  schema = StructType([
    StructField('activities', StringType(), True), 
    StructField('activities_0_timePercents', IntegerType(), True),
    StructField('activities_0_title', StringType(), True),
    StructField('activities_1_timePercents', IntegerType(), True),
    StructField('activities_1_title', StringType(), True),
    StructField('activities_2_timePercents', IntegerType(), True),
    StructField('activities_2_title', StringType(), True),
    StructField('activities_3_timePercents', IntegerType(), True),
    StructField('activities_3_title', StringType(), True),
    StructField('activities_4_timePercents', IntegerType(), True),
    StructField('activities_4_title', StringType(), True),
    StructField('activities_5_timePercents', IntegerType(), True),
    StructField('activities_5_title', StringType(), True),
    StructField('activities_6_timePercents', IntegerType(), True),
    StructField('activities_6_title', StringType(), True),
    StructField('benefits', StringType(), True),
    StructField('benefits_0_icon', StringType(), True),
    StructField('benefits_0_title', StringType(), True),
    StructField('benefits_10_icon', StringType(), True),
    StructField('benefits_10_title', StringType(), True),
    StructField('benefits_11_icon', StringType(), True),
    StructField('benefits_11_title', StringType(), True),
    StructField('benefits_12_icon', StringType(), True),
    StructField('benefits_12_title', StringType(), True),
    StructField('benefits_13_icon', StringType(), True),
    StructField('benefits_13_title', StringType(), True),
    StructField('benefits_14_icon', StringType(), True),
    StructField('benefits_14_title', StringType(), True),
    StructField('benefits_15_icon', StringType(), True),
    StructField('benefits_15_title', StringType(), True),
    StructField('benefits_16_icon', StringType(), True),
    StructField('benefits_16_title', StringType(), True),
    StructField('benefits_17_icon', StringType(), True),
    StructField('benefits_17_title', StringType(), True),
    StructField('benefits_18_icon', StringType(), True),
    StructField('benefits_18_title', StringType(), True),
    StructField('benefits_19_icon', StringType(), True),
    StructField('benefits_19_title', StringType(), True),
    StructField('benefits_1_icon', StringType(), True),
    StructField('benefits_1_title', StringType(), True),
    StructField('benefits_20_icon', StringType(), True),
    StructField('benefits_20_title', StringType(), True),
    StructField('benefits_21_icon', StringType(), True),
    StructField('benefits_21_title', StringType(), True),
    StructField('benefits_22_icon', StringType(), True),
    StructField('benefits_22_title', StringType(), True),
    StructField('benefits_23_icon', StringType(), True),
    StructField('benefits_23_title', StringType(), True),
    StructField('benefits_24_icon', StringType(), True),
    StructField('benefits_24_title', StringType(), True),
    StructField('benefits_25_icon', StringType(), True),
    StructField('benefits_25_title', StringType(), True),
    StructField('benefits_26_icon', StringType(), True),
    StructField('benefits_26_title', StringType(), True),
    StructField('benefits_27_icon', StringType(), True),
    StructField('benefits_27_title', StringType(), True),
    StructField('benefits_28_icon', StringType(), True),
    StructField('benefits_28_title', StringType(), True),
    StructField('benefits_29_icon', StringType(), True),
    StructField('benefits_29_title', StringType(), True),
    StructField('benefits_2_icon', StringType(), True),
    StructField('benefits_2_title', StringType(), True),
    StructField('benefits_30_icon', StringType(), True),
    StructField('benefits_30_title', StringType(), True),
    StructField('benefits_3_icon', StringType(), True),
    StructField('benefits_3_title', StringType(), True),
    StructField('benefits_4_icon', StringType(), True),
    StructField('benefits_4_title', StringType(), True),
    StructField('benefits_5_icon', StringType(), True),
    StructField('benefits_5_title', StringType(), True),
    StructField('benefits_6_icon', StringType(), True),
    StructField('benefits_6_title', StringType(), True),
    StructField('benefits_7_icon', StringType(), True),
    StructField('benefits_7_title', StringType(), True),
    StructField('benefits_8_icon', StringType(), True),
    StructField('benefits_8_title', StringType(), True),
    StructField('benefits_9_icon', StringType(), True),
    StructField('benefits_9_title', StringType(), True),
    StructField('businessTravelComment', StringType(), True),
    StructField('businessTraveling', BooleanType(), True),
    StructField('companyId', IntegerType(), True),
    StructField('company_awards', StringType(), True),
    StructField('company_awards_0_icon', StringType(), True),
    StructField('company_awards_0_title', StringType(), True),
    StructField('company_awards_1_icon', StringType(), True),
    StructField('company_awards_1_title', StringType(), True),
    StructField('company_awards_2_icon', StringType(), True),
    StructField('company_awards_2_title', StringType(), True),
    StructField('company_awards_3_icon', StringType(), True),
    StructField('company_awards_3_title', StringType(), True),
    StructField('company_awards_4_icon', StringType(), True),
    StructField('company_awards_4_title', StringType(), True),
    StructField('company_awards_5_icon', StringType(), True),
    StructField('company_awards_5_title', StringType(), True),
    StructField('company_awards_6_icon', StringType(), True),
    StructField('company_awards_6_title', StringType(), True),
    StructField('company_awards_7_icon', StringType(), True),
    StructField('company_awards_7_title', StringType(), True),
    StructField('company_awards_8_icon', StringType(), True),
    StructField('company_awards_8_title', StringType(), True),
    StructField('company_brand', StringType(), True),
    StructField('company_id', IntegerType(), True),
    StructField('company_images_0_collection', StringType(), True),
    StructField('company_images_0_id', IntegerType(), True),
    StructField('company_images_0_name', StringType(), True),
    StructField('company_images_10_collection', StringType(), True),
    StructField('company_images_10_id', IntegerType(), True),
    StructField('company_images_10_name', StringType(), True),
    StructField('company_images_11_collection', StringType(), True),
    StructField('company_images_11_id', IntegerType(), True),
    StructField('company_images_11_name', StringType(), True),
    StructField('company_images_12_collection', StringType(), True),
    StructField('company_images_12_id', IntegerType(), True),
    StructField('company_images_12_name', StringType(), True),
    StructField('company_images_13_collection', StringType(), True),
    StructField('company_images_13_id', IntegerType(), True),
    StructField('company_images_13_name', StringType(), True),
    StructField('company_images_14_collection', StringType(), True),
    StructField('company_images_14_id', IntegerType(), True),
    StructField('company_images_14_name', StringType(), True),
    StructField('company_images_15_collection', StringType(), True),
    StructField('company_images_15_id', IntegerType(), True),
    StructField('company_images_15_name', StringType(), True),
    StructField('company_images_16_collection', StringType(), True),
    StructField('company_images_16_id', IntegerType(), True),
    StructField('company_images_16_name', StringType(), True),
    StructField('company_images_17_collection', StringType(), True),
    StructField('company_images_17_id', IntegerType(), True),
    StructField('company_images_17_name', StringType(), True),
    StructField('company_images_18_collection', StringType(), True),
    StructField('company_images_18_id', IntegerType(), True),
    StructField('company_images_18_name', StringType(), True),
    StructField('company_images_19_collection', StringType(), True),
    StructField('company_images_19_id', IntegerType(), True),
    StructField('company_images_19_name', StringType(), True),
    StructField('company_images_1_collection', StringType(), True),
    StructField('company_images_1_id', IntegerType(), True),
    StructField('company_images_1_name', StringType(), True),
    StructField('company_images_20_collection', StringType(), True),
    StructField('company_images_20_id', IntegerType(), True),
    StructField('company_images_20_name', StringType(), True),
    StructField('company_images_21_collection', StringType(), True),
    StructField('company_images_21_id', IntegerType(), True),
    StructField('company_images_21_name', StringType(), True),
    StructField('company_images_22_collection', StringType(), True),
    StructField('company_images_22_id', IntegerType(), True),
    StructField('company_images_22_name', StringType(), True),
    StructField('company_images_23_collection', StringType(), True),
    StructField('company_images_23_id', IntegerType(), True),
    StructField('company_images_23_name', StringType(), True),
    StructField('company_images_24_collection', StringType(), True),
    StructField('company_images_24_id', IntegerType(), True),
    StructField('company_images_24_name', StringType(), True),
    StructField('company_images_25_collection', StringType(), True),
    StructField('company_images_25_id', IntegerType(), True),
    StructField('company_images_25_name', StringType(), True),
    StructField('company_images_26_collection', StringType(), True),
    StructField('company_images_26_id', IntegerType(), True),
    StructField('company_images_26_name', StringType(), True),
    StructField('company_images_27_collection', StringType(), True),
    StructField('company_images_27_id', IntegerType(), True),
    StructField('company_images_27_name', StringType(), True),
    StructField('company_images_28_collection', StringType(), True),
    StructField('company_images_28_id', IntegerType(), True),
    StructField('company_images_28_name', StringType(), True),
    StructField('company_images_29_collection', StringType(), True),
    StructField('company_images_29_id', IntegerType(), True),
    StructField('company_images_29_name', StringType(), True),
    StructField('company_images_2_collection', StringType(), True),
    StructField('company_images_2_id', IntegerType(), True),
    StructField('company_images_2_name', StringType(), True),
    StructField('company_images_30_collection', StringType(), True),
    StructField('company_images_30_id', IntegerType(), True),
    StructField('company_images_30_name', StringType(), True),
    StructField('company_images_31_collection', StringType(), True),
    StructField('company_images_31_id', IntegerType(), True),
    StructField('company_images_31_name', StringType(), True),
    StructField('company_images_32_collection', StringType(), True),
    StructField('company_images_32_id', IntegerType(), True),
    StructField('company_images_32_name', StringType(), True),
    StructField('company_images_33_collection', StringType(), True),
    StructField('company_images_33_id', IntegerType(), True),
    StructField('company_images_33_name', StringType(), True),
    StructField('company_images_34_collection', StringType(), True),
    StructField('company_images_34_id', IntegerType(), True),
    StructField('company_images_34_name', StringType(), True),
    StructField('company_images_35_collection', StringType(), True),
    StructField('company_images_35_id', IntegerType(), True),
    StructField('company_images_35_name', StringType(), True),
    StructField('company_images_36_collection', StringType(), True),
    StructField('company_images_36_id', IntegerType(), True),
    StructField('company_images_36_name', StringType(), True),
    StructField('company_images_37_collection', StringType(), True),
    StructField('company_images_37_id', IntegerType(), True),
    StructField('company_images_37_name', StringType(), True),
    StructField('company_images_38_collection', StringType(), True),
    StructField('company_images_38_id', IntegerType(), True),
    StructField('company_images_38_name', StringType(), True),
    StructField('company_images_39_collection', StringType(), True),
    StructField('company_images_39_id', IntegerType(), True),
    StructField('company_images_39_name', StringType(), True),
    StructField('company_images_3_collection', StringType(), True),
    StructField('company_images_3_id', IntegerType(), True),
    StructField('company_images_3_name', StringType(), True),
    StructField('company_images_40_collection', StringType(), True),
    StructField('company_images_40_id', IntegerType(), True),
    StructField('company_images_40_name', StringType(), True),
    StructField('company_images_41_collection', StringType(), True),
    StructField('company_images_41_id', IntegerType(), True),
    StructField('company_images_41_name', StringType(), True),
    StructField('company_images_42_collection', StringType(), True),
    StructField('company_images_42_id', IntegerType(), True),
    StructField('company_images_42_name', StringType(), True),
    StructField('company_images_43_collection', StringType(), True),
    StructField('company_images_43_id', IntegerType(), True),
    StructField('company_images_43_name', StringType(), True),
    StructField('company_images_44_collection', StringType(), True),
    StructField('company_images_44_id', IntegerType(), True),
    StructField('company_images_44_name', StringType(), True),
    StructField('company_images_45_collection', StringType(), True),
    StructField('company_images_45_id', IntegerType(), True),
    StructField('company_images_45_name', StringType(), True),
    StructField('company_images_46_collection', StringType(), True),
    StructField('company_images_46_id', IntegerType(), True),
    StructField('company_images_46_name', StringType(), True),
    StructField('company_images_47_collection', StringType(), True),
    StructField('company_images_47_id', IntegerType(), True),
    StructField('company_images_47_name', StringType(), True),
    StructField('company_images_48_collection', StringType(), True),
    StructField('company_images_48_id', IntegerType(), True),
    StructField('company_images_48_name', StringType(), True),
    StructField('company_images_49_collection', StringType(), True),
    StructField('company_images_49_id', IntegerType(), True),
    StructField('company_images_49_name', StringType(), True),
    StructField('company_images_4_collection', StringType(), True),
    StructField('company_images_4_id', IntegerType(), True),
    StructField('company_images_4_name', StringType(), True),
    StructField('company_images_50_collection', StringType(), True),
    StructField('company_images_50_id', IntegerType(), True),
    StructField('company_images_50_name', StringType(), True),
    StructField('company_images_51_collection', StringType(), True),
    StructField('company_images_51_id', IntegerType(), True),
    StructField('company_images_51_name', StringType(), True),
    StructField('company_images_52_collection', StringType(), True),
    StructField('company_images_52_id', IntegerType(), True),
    StructField('company_images_52_name', StringType(), True),
    StructField('company_images_53_collection', StringType(), True),
    StructField('company_images_53_id', IntegerType(), True),
    StructField('company_images_53_name', StringType(), True),
    StructField('company_images_54_collection', StringType(), True),
    StructField('company_images_54_id', IntegerType(), True),
    StructField('company_images_54_name', StringType(), True),
    StructField('company_images_55_collection', StringType(), True),
    StructField('company_images_55_id', IntegerType(), True),
    StructField('company_images_55_name', StringType(), True),
    StructField('company_images_56_collection', StringType(), True),
    StructField('company_images_56_id', IntegerType(), True),
    StructField('company_images_56_name', StringType(), True),
    StructField('company_images_57_collection', StringType(), True),
    StructField('company_images_57_id', IntegerType(), True),
    StructField('company_images_57_name', StringType(), True),
    StructField('company_images_58_collection', StringType(), True),
    StructField('company_images_58_id', IntegerType(), True),
    StructField('company_images_58_name', StringType(), True),
    StructField('company_images_59_collection', StringType(), True),
    StructField('company_images_59_id', IntegerType(), True),
    StructField('company_images_59_name', StringType(), True),
    StructField('company_images_5_collection', StringType(), True),
    StructField('company_images_5_id', IntegerType(), True),
    StructField('company_images_5_name', StringType(), True),
    StructField('company_images_60_collection', StringType(), True),
    StructField('company_images_60_id', IntegerType(), True),
    StructField('company_images_60_name', StringType(), True),
    StructField('company_images_61_collection', StringType(), True),
    StructField('company_images_61_id', IntegerType(), True),
    StructField('company_images_61_name', StringType(), True),
    StructField('company_images_62_collection', StringType(), True),
    StructField('company_images_62_id', IntegerType(), True),
    StructField('company_images_62_name', StringType(), True),
    StructField('company_images_63_collection', StringType(), True),
    StructField('company_images_63_id', IntegerType(), True),
    StructField('company_images_63_name', StringType(), True),
    StructField('company_images_64_collection', StringType(), True),
    StructField('company_images_64_id', IntegerType(), True),
    StructField('company_images_64_name', StringType(), True),
    StructField('company_images_65_collection', StringType(), True),
    StructField('company_images_65_id', IntegerType(), True),
    StructField('company_images_65_name', StringType(), True),
    StructField('company_images_66_collection', StringType(), True),
    StructField('company_images_66_id', IntegerType(), True),
    StructField('company_images_66_name', StringType(), True),
    StructField('company_images_67_collection', StringType(), True),
    StructField('company_images_67_id', IntegerType(), True),
    StructField('company_images_67_name', StringType(), True),
    StructField('company_images_68_collection', StringType(), True),
    StructField('company_images_68_id', IntegerType(), True),
    StructField('company_images_68_name', StringType(), True),
    StructField('company_images_69_collection', StringType(), True),
    StructField('company_images_69_id', IntegerType(), True),
    StructField('company_images_69_name', StringType(), True),
    StructField('company_images_6_collection', StringType(), True),
    StructField('company_images_6_id', IntegerType(), True),
    StructField('company_images_6_name', StringType(), True),
    StructField('company_images_70_collection', StringType(), True),
    StructField('company_images_70_id', IntegerType(), True),
    StructField('company_images_70_name', StringType(), True),
    StructField('company_images_71_collection', StringType(), True),
    StructField('company_images_71_id', IntegerType(), True),
    StructField('company_images_71_name', StringType(), True),
    StructField('company_images_72_collection', StringType(), True),
    StructField('company_images_72_id', IntegerType(), True),
    StructField('company_images_72_name', StringType(), True),
    StructField('company_images_73_collection', StringType(), True),
    StructField('company_images_73_id', IntegerType(), True),
    StructField('company_images_73_name', StringType(), True),
    StructField('company_images_74_collection', StringType(), True),
    StructField('company_images_74_id', IntegerType(), True),
    StructField('company_images_74_name', StringType(), True),
    StructField('company_images_75_collection', StringType(), True),
    StructField('company_images_75_id', IntegerType(), True),
    StructField('company_images_75_name', StringType(), True),
    StructField('company_images_76_collection', StringType(), True),
    StructField('company_images_76_id', IntegerType(), True),
    StructField('company_images_76_name', StringType(), True),
    StructField('company_images_77_collection', StringType(), True),
    StructField('company_images_77_id', IntegerType(), True),
    StructField('company_images_77_name', StringType(), True),
    StructField('company_images_78_collection', StringType(), True),
    StructField('company_images_78_id', IntegerType(), True),
    StructField('company_images_78_name', StringType(), True),
    StructField('company_images_79_collection', StringType(), True),
    StructField('company_images_79_id', IntegerType(), True),
    StructField('company_images_79_name', StringType(), True),
    StructField('company_images_7_collection', StringType(), True),
    StructField('company_images_7_id', IntegerType(), True),
    StructField('company_images_7_name', StringType(), True),
    StructField('company_images_80_collection', StringType(), True),
    StructField('company_images_80_id', IntegerType(), True),
    StructField('company_images_80_name', StringType(), True),
    StructField('company_images_8_collection', StringType(), True),
    StructField('company_images_8_id', IntegerType(), True),
    StructField('company_images_8_name', StringType(), True),
    StructField('company_images_9_collection', StringType(), True),
    StructField('company_images_9_id', IntegerType(), True),
    StructField('company_images_9_name', StringType(), True),
    StructField('company_locations_0_address', StringType(), True),
    StructField('company_locations_0_comment', StringType(), True),
    StructField('company_locations_0_founded', IntegerType(), True),
    StructField('company_locations_0_id', IntegerType(), True),
    StructField('company_locations_0_teamSize', StringType(), True),
    StructField('company_locations_10_address', StringType(), True),
    StructField('company_locations_10_comment', StringType(), True),
    StructField('company_locations_10_founded', IntegerType(), True),
    StructField('company_locations_10_id', IntegerType(), True),
    StructField('company_locations_10_teamSize', StringType(), True),
    StructField('company_locations_11_address', StringType(), True),
    StructField('company_locations_11_comment', StringType(), True),
    StructField('company_locations_11_founded', StringType(), True),
    StructField('company_locations_11_id', IntegerType(), True),
    StructField('company_locations_11_teamSize', StringType(), True),
    StructField('company_locations_12_address', StringType(), True),
    StructField('company_locations_12_comment', StringType(), True),
    StructField('company_locations_12_founded', StringType(), True),
    StructField('company_locations_12_id', IntegerType(), True),
    StructField('company_locations_12_teamSize', StringType(), True),
    StructField('company_locations_13_address', StringType(), True),
    StructField('company_locations_13_comment', StringType(), True),
    StructField('company_locations_13_founded', StringType(), True),
    StructField('company_locations_13_id', IntegerType(), True),
    StructField('company_locations_13_teamSize', StringType(), True),
    StructField('company_locations_14_address', StringType(), True),
    StructField('company_locations_14_comment', StringType(), True),
    StructField('company_locations_14_founded', StringType(), True),
    StructField('company_locations_14_id', IntegerType(), True),
    StructField('company_locations_14_teamSize', StringType(), True),
    StructField('company_locations_15_address', StringType(), True),
    StructField('company_locations_15_comment', StringType(), True),
    StructField('company_locations_15_founded', StringType(), True),
    StructField('company_locations_15_id', IntegerType(), True),
    StructField('company_locations_15_teamSize', StringType(), True),
    StructField('company_locations_16_address', StringType(), True),
    StructField('company_locations_16_comment', StringType(), True),
    StructField('company_locations_16_founded', StringType(), True),
    StructField('company_locations_16_id', IntegerType(), True),
    StructField('company_locations_16_teamSize', StringType(), True),
    StructField('company_locations_1_address', StringType(), True),
    StructField('company_locations_1_comment', StringType(), True),
    StructField('company_locations_1_founded', IntegerType(), True),
    StructField('company_locations_1_id', IntegerType(), True),
    StructField('company_locations_1_teamSize', StringType(), True),
    StructField('company_locations_2_address', StringType(), True),
    StructField('company_locations_2_comment', StringType(), True),
    StructField('company_locations_2_founded', IntegerType(), True),
    StructField('company_locations_2_id', IntegerType(), True),
    StructField('company_locations_2_teamSize', StringType(), True),
    StructField('company_locations_3_address', StringType(), True),
    StructField('company_locations_3_comment', StringType(), True),
    StructField('company_locations_3_founded', IntegerType(), True),
    StructField('company_locations_3_id', IntegerType(), True),
    StructField('company_locations_3_teamSize', StringType(), True),
    StructField('company_locations_4_address', StringType(), True),
    StructField('company_locations_4_comment', StringType(), True),
    StructField('company_locations_4_founded', IntegerType(), True),
    StructField('company_locations_4_id', IntegerType(), True),
    StructField('company_locations_4_teamSize', StringType(), True),
    StructField('company_locations_5_address', StringType(), True),
    StructField('company_locations_5_comment', StringType(), True),
    StructField('company_locations_5_founded', IntegerType(), True),
    StructField('company_locations_5_id', IntegerType(), True),
    StructField('company_locations_5_teamSize', StringType(), True),
    StructField('company_locations_6_address', StringType(), True),
    StructField('company_locations_6_comment', StringType(), True),
    StructField('company_locations_6_founded', IntegerType(), True),
    StructField('company_locations_6_id', IntegerType(), True),
    StructField('company_locations_6_teamSize', StringType(), True),
    StructField('company_locations_7_address', StringType(), True),
    StructField('company_locations_7_comment', StringType(), True),
    StructField('company_locations_7_founded', IntegerType(), True),
    StructField('company_locations_7_id', IntegerType(), True),
    StructField('company_locations_7_teamSize', StringType(), True),
    StructField('company_locations_8_address', StringType(), True),
    StructField('company_locations_8_comment', StringType(), True),
    StructField('company_locations_8_founded', IntegerType(), True),
    StructField('company_locations_8_id', IntegerType(), True),
    StructField('company_locations_8_teamSize', StringType(), True),
    StructField('company_locations_9_address', StringType(), True),
    StructField('company_locations_9_comment', StringType(), True),
    StructField('company_locations_9_founded', IntegerType(), True),
    StructField('company_locations_9_id', IntegerType(), True),
    StructField('company_locations_9_teamSize', StringType(), True),
    StructField('company_overview', StringType(), True),
    StructField('company_perks', StringType(), True),
    StructField('company_perks_0_icon', StringType(), True),
    StructField('company_perks_0_text', StringType(), True),
    StructField('company_perks_0_title', StringType(), True),
    StructField('company_perks_10_icon', StringType(), True),
    StructField('company_perks_10_text', StringType(), True),
    StructField('company_perks_10_title', StringType(), True),
    StructField('company_perks_11_icon', StringType(), True),
    StructField('company_perks_11_text', StringType(), True),
    StructField('company_perks_11_title', StringType(), True),
    StructField('company_perks_12_icon', StringType(), True),
    StructField('company_perks_12_text', StringType(), True),
    StructField('company_perks_12_title', StringType(), True),
    StructField('company_perks_13_icon', StringType(), True),
    StructField('company_perks_13_text', StringType(), True),
    StructField('company_perks_13_title', StringType(), True),
    StructField('company_perks_14_icon', StringType(), True),
    StructField('company_perks_14_text', StringType(), True),
    StructField('company_perks_14_title', StringType(), True),
    StructField('company_perks_15_icon', StringType(), True),
    StructField('company_perks_15_text', StringType(), True),
    StructField('company_perks_15_title', StringType(), True),
    StructField('company_perks_16_icon', StringType(), True),
    StructField('company_perks_16_text', StringType(), True),
    StructField('company_perks_16_title', StringType(), True),
    StructField('company_perks_17_icon', StringType(), True),
    StructField('company_perks_17_text', StringType(), True),
    StructField('company_perks_17_title', StringType(), True),
    StructField('company_perks_1_icon', StringType(), True),
    StructField('company_perks_1_text', StringType(), True),
    StructField('company_perks_1_title', StringType(), True),
    StructField('company_perks_2_icon', StringType(), True),
    StructField('company_perks_2_text', StringType(), True),
    StructField('company_perks_2_title', StringType(), True),
    StructField('company_perks_3_icon', StringType(), True),
    StructField('company_perks_3_text', StringType(), True),
    StructField('company_perks_3_title', StringType(), True),
    StructField('company_perks_4_icon', StringType(), True),
    StructField('company_perks_4_text', StringType(), True),
    StructField('company_perks_4_title', StringType(), True),
    StructField('company_perks_5_icon', StringType(), True),
    StructField('company_perks_5_text', StringType(), True),
    StructField('company_perks_5_title', StringType(), True),
    StructField('company_perks_6_icon', StringType(), True),
    StructField('company_perks_6_text', StringType(), True),
    StructField('company_perks_6_title', StringType(), True),
    StructField('company_perks_7_icon', StringType(), True),
    StructField('company_perks_7_text', StringType(), True),
    StructField('company_perks_7_title', StringType(), True),
    StructField('company_perks_8_icon', StringType(), True),
    StructField('company_perks_8_text', StringType(), True),
    StructField('company_perks_8_title', StringType(), True),
    StructField('company_perks_9_icon', StringType(), True),
    StructField('company_perks_9_text', StringType(), True),
    StructField('company_perks_9_title', StringType(), True),
    StructField('company_product', StringType(), True),
    StructField('company_public', BooleanType(), True),
    StructField('company_slug', StringType(), True),
    StructField('company_values', StringType(), True),
    StructField('company_values_0_icon', StringType(), True),
    StructField('company_values_0_text', StringType(), True),
    StructField('company_values_0_title', StringType(), True),
    StructField('company_values_1_icon', StringType(), True),
    StructField('company_values_1_text', StringType(), True),
    StructField('company_values_1_title', StringType(), True),
    StructField('company_values_2_icon', StringType(), True),
    StructField('company_values_2_text', StringType(), True),
    StructField('company_values_2_title', StringType(), True),
    StructField('company_values_3_icon', StringType(), True),
    StructField('company_values_3_text', StringType(), True),
    StructField('company_values_3_title', StringType(), True),
    StructField('company_values_4_icon', StringType(), True),
    StructField('company_values_4_text', StringType(), True),
    StructField('company_values_4_title', StringType(), True),
    StructField('company_values_5_icon', StringType(), True),
    StructField('company_values_5_text', StringType(), True),
    StructField('company_values_5_title', StringType(), True),
    StructField('company_values_6_icon', StringType(), True),
    StructField('company_values_6_text', StringType(), True),
    StructField('company_values_6_title', StringType(), True),
    StructField('company_values_7_icon', StringType(), True),
    StructField('company_values_7_text', StringType(), True),
    StructField('company_values_7_title', StringType(), True),
    StructField('company_values_8_icon', StringType(), True),
    StructField('company_values_8_text', StringType(), True),
    StructField('company_values_8_title', StringType(), True),
    StructField('company_values_9_icon', StringType(), True),
    StructField('company_values_9_text', StringType(), True),
    StructField('company_values_9_title', StringType(), True),
    StructField('customerFacing', BooleanType(), True),
    StructField('description', StringType(), True),
    StructField('fullyRemote', BooleanType(), True),
    StructField('hiringProcessSteps', StringType(), True),
    StructField('hiringProcessSteps_0', StringType(), True),
    StructField('hiringProcessSteps_1', StringType(), True),
    StructField('hiringProcessSteps_2', StringType(), True),
    StructField('hiringProcessSteps_3', StringType(), True),
    StructField('hiringProcessSteps_4', StringType(), True),
    StructField('hiringProcessSteps_5', StringType(), True),
    StructField('homeOfficeDays', IntegerType(), True),
    StructField('homeOfficePer', StringType(), True),
    StructField('id', IntegerType(), True),
    StructField('jobType', StringType(), True),
    StructField('jobTypeComment', StringType(), True),
    StructField('locations', StringType(), True),
    StructField('locations_0_address', StringType(), True),
    StructField('locations_0_comment', StringType(), True),
    StructField('locations_0_founded', IntegerType(), True),
    StructField('locations_0_id', IntegerType(), True),
    StructField('locations_0_teamSize', StringType(), True),
    StructField('locations_1_address', StringType(), True),
    StructField('locations_1_comment', StringType(), True),
    StructField('locations_1_founded', IntegerType(), True),
    StructField('locations_1_id', IntegerType(), True),
    StructField('locations_1_teamSize', StringType(), True),
    StructField('locations_2_address', StringType(), True),
    StructField('locations_2_comment', StringType(), True),
    StructField('locations_2_founded', IntegerType(), True),
    StructField('locations_2_id', IntegerType(), True),
    StructField('locations_2_teamSize', StringType(), True),
    StructField('locations_3_address', StringType(), True),
    StructField('locations_3_comment', StringType(), True),
    StructField('locations_3_founded', IntegerType(), True),
    StructField('locations_3_id', IntegerType(), True),
    StructField('locations_3_teamSize', StringType(), True),
    StructField('locations_4_address', StringType(), True),
    StructField('locations_4_comment', StringType(), True),
    StructField('locations_4_founded', IntegerType(), True),
    StructField('locations_4_id', IntegerType(), True),
    StructField('locations_4_teamSize', StringType(), True),
    StructField('mainDatabase', StringType(), True),
    StructField('offeringStock', BooleanType(), True),
    StructField('postedAt', IntegerType(), True),
    StructField('primaryLanguage', StringType(), True),
    StructField('primaryPlatform', StringType(), True),
    StructField('productDescription', StringType(), True),
    StructField('productImages', StringType(), True),
    StructField('productImages_0_collection', StringType(), True),
    StructField('productImages_0_id', IntegerType(), True),
    StructField('productImages_0_name', StringType(), True),
    StructField('productImages_1_collection', StringType(), True),
    StructField('productImages_1_id', IntegerType(), True),
    StructField('productImages_1_name', StringType(), True),
    StructField('productImages_2_collection', StringType(), True),
    StructField('productImages_2_id', IntegerType(), True),
    StructField('productImages_2_name', StringType(), True),
    StructField('productImages_3_collection', StringType(), True),
    StructField('productImages_3_id', IntegerType(), True),
    StructField('productImages_3_name', StringType(), True),
    StructField('productImages_4_collection', StringType(), True),
    StructField('productImages_4_id', IntegerType(), True),
    StructField('productImages_4_name', StringType(), True),
    StructField('productImages_5_collection', StringType(), True),
    StructField('productImages_5_id', IntegerType(), True),
    StructField('productImages_5_name', StringType(), True),
    StructField('productImages_6_collection', StringType(), True),
    StructField('productImages_6_id', IntegerType(), True),
    StructField('productImages_6_name', StringType(), True),
    StructField('productImages_7_collection', StringType(), True),
    StructField('productImages_7_id', IntegerType(), True),
    StructField('productImages_7_name', StringType(), True),
    StructField('public', BooleanType(), True),
    StructField('requirements_0_icon', StringType(), True),
    StructField('requirements_0_title', StringType(), True),
    StructField('requirements_10_icon', StringType(), True),
    StructField('requirements_10_title', StringType(), True),
    StructField('requirements_11_icon', StringType(), True),
    StructField('requirements_11_title', StringType(), True),
    StructField('requirements_12_icon', StringType(), True),
    StructField('requirements_12_title', StringType(), True),
    StructField('requirements_13_icon', StringType(), True),
    StructField('requirements_13_title', StringType(), True),
    StructField('requirements_1_icon', StringType(), True),
    StructField('requirements_1_title', StringType(), True),
    StructField('requirements_2_icon', StringType(), True),
    StructField('requirements_2_title', StringType(), True),
    StructField('requirements_3_icon', StringType(), True),
    StructField('requirements_3_title', StringType(), True),
    StructField('requirements_4_icon', StringType(), True),
    StructField('requirements_4_title', StringType(), True),
    StructField('requirements_5_icon', StringType(), True),
    StructField('requirements_5_title', StringType(), True),
    StructField('requirements_6_icon', StringType(), True),
    StructField('requirements_6_title', StringType(), True),
    StructField('requirements_7_icon', StringType(), True),
    StructField('requirements_7_title', StringType(), True),
    StructField('requirements_8_icon', StringType(), True),
    StructField('requirements_8_title', StringType(), True),
    StructField('requirements_9_icon', StringType(), True),
    StructField('requirements_9_title', StringType(), True),
    StructField('responsibilities_0_icon', StringType(), True),
    StructField('responsibilities_0_title', StringType(), True),
    StructField('responsibilities_10_icon', StringType(), True),
    StructField('responsibilities_10_title', StringType(), True),
    StructField('responsibilities_11_icon', StringType(), True),
    StructField('responsibilities_11_title', StringType(), True),
    StructField('responsibilities_12_icon', StringType(), True),
    StructField('responsibilities_12_title', StringType(), True),
    StructField('responsibilities_13_icon', StringType(), True),
    StructField('responsibilities_13_title', StringType(), True),
    StructField('responsibilities_14_icon', StringType(), True),
    StructField('responsibilities_14_title', StringType(), True),
    StructField('responsibilities_15_icon', StringType(), True),
    StructField('responsibilities_15_title', StringType(), True),
    StructField('responsibilities_16_icon', StringType(), True),
    StructField('responsibilities_16_title', StringType(), True),
    StructField('responsibilities_17_icon', StringType(), True),
    StructField('responsibilities_17_title', StringType(), True),
    StructField('responsibilities_1_icon', StringType(), True),
    StructField('responsibilities_1_title', StringType(), True),
    StructField('responsibilities_2_icon', StringType(), True),
    StructField('responsibilities_2_title', StringType(), True),
    StructField('responsibilities_3_icon', StringType(), True),
    StructField('responsibilities_3_title', StringType(), True),
    StructField('responsibilities_4_icon', StringType(), True),
    StructField('responsibilities_4_title', StringType(), True),
    StructField('responsibilities_5_icon', StringType(), True),
    StructField('responsibilities_5_title', StringType(), True),
    StructField('responsibilities_6_icon', StringType(), True),
    StructField('responsibilities_6_title', StringType(), True),
    StructField('responsibilities_7_icon', StringType(), True),
    StructField('responsibilities_7_title', StringType(), True),
    StructField('responsibilities_8_icon', StringType(), True),
    StructField('responsibilities_8_title', StringType(), True),
    StructField('responsibilities_9_icon', StringType(), True),
    StructField('responsibilities_9_title', StringType(), True),
    StructField('role', StringType(), True),
    StructField('salaryCurrency', StringType(), True),
    StructField('salaryMax', IntegerType(), True),
    StructField('salaryMin', IntegerType(), True),
    StructField('salaryPeriod', StringType(), True),
    StructField('secondaryLanguage', StringType(), True),
    StructField('secondaryPlatform', StringType(), True),
    StructField('seniority', StringType(), True),
    StructField('slug', StringType(), True),
    StructField('teamLead', StringType(), True),
    StructField('teamLeadImage', StringType(), True),
    StructField('teamLeadImage_collection', StringType(), True),
    StructField('teamLeadImage_id', IntegerType(), True),
    StructField('teamLeadImage_name', StringType(), True),
    StructField('teamLeadName', StringType(), True),
    StructField('teamLeadRole', StringType(), True),
    StructField('teamSizeMax', IntegerType(), True),
    StructField('teamSizeMin', IntegerType(), True),
    StructField('title', StringType(), True),
    StructField('tools', StringType(), True),
    StructField('tools_0', StringType(), True),
    StructField('tools_1', StringType(), True),
    StructField('tools_10', StringType(), True),
    StructField('tools_11', StringType(), True),
    StructField('tools_12', StringType(), True),
    StructField('tools_13', StringType(), True),
    StructField('tools_14', StringType(), True),
    StructField('tools_15', StringType(), True),
    StructField('tools_16', StringType(), True),
    StructField('tools_17', StringType(), True),
    StructField('tools_18', StringType(), True),
    StructField('tools_19', StringType(), True),
    StructField('tools_2', StringType(), True),
    StructField('tools_3', StringType(), True),
    StructField('tools_4', StringType(), True),
    StructField('tools_5', StringType(), True),
    StructField('tools_6', StringType(), True),
    StructField('tools_7', StringType(), True),
    StructField('tools_8', StringType(), True),
    StructField('tools_9', StringType(), True)
])

# COMMAND ----------

df.select(*[column for column in df.columns if "address" in column]).display()

# COMMAND ----------

# MAGIC %md
# MAGIC # End of Testing Section

# COMMAND ----------

# DBTITLE 1,Write to ADLS Raw
# Create target location
dbutils.fs.mkdirs(main_path + posts_path)
print(f"Created: {main_path + posts_path}")

# Since the raw data has more than 700 columns and above 300 of them are useless (e.g. icons and images ids), 
# some of the will be droped in order to decrease the raw file size.
df_posts = pd.DataFrame.from_dict(flatten_posts_list)
columns_to_drop = [c for c in df_posts.columns if "icon" in c.lower() or "images" in c.lower() or "image" in c.lower()]
df_posts = df_posts.drop(columns=columns_to_drop)

# Write the Posts DataFrame to ADLS, raw location
df_posts.to_csv(location_prefix + main_path + posts_path + posts_file_name)
print(f"Saved at: {location_prefix + main_path + posts_path + posts_file_name}")

# COMMAND ----------

# df_posts["description"] = df_posts["description"].str.replace(r'<[^<>]*>', '', regex=True)

# COMMAND ----------

# for i in df_posts["description"]:
#     print(i)
#     print("------------------------------------------NEXT------------------------------------------")

# COMMAND ----------

# for i in df_posts["company"]:
#     print(i)
#     print("------------------------------------------NEXT------------------------------------------")
