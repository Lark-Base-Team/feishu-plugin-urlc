from baseopensdk import BaseClient
from baseopensdk.api.base.v1 import *
from baseopensdk.api.drive.v1 import *

from playground.rmbg_demo import remove_image_bg

import os
import json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

APP_TOKEN = os.environ['APP_TOKEN']
PERSONAL_BASE_TOKEN = os.environ['PERSONAL_BASE_TOKEN']
TABLE_ID = os.environ['TABLE_ID']


def search_and_replace_func(source: str, target: str):

  # 1. build a client
  client: BaseClient = BaseClient.builder() \
    .app_token(APP_TOKEN) \
    .personal_base_token(PERSONAL_BASE_TOKEN) \
    .build()

  # 文件下载=====
  # 高级权限鉴权信息 文档未开启高级权限则无需传 extra 字段
  # [{"name":"DALL·E 2023-12-01 11.34.33 - An illustration in Pixar or Disney style depicting a scene from a classic Chinese tale. The image shows a brave, young boy, Nezha, with a determined e.png","size":3550733,"type":"image/png","token":"OA8pbQSIUoucfYxWNtfcXArqnBc","timeStamp":1701401695621,"permission":{"tableId":"tblsbCJnrsLMNrms","fieldId":"fldSP3jGD4","recordId":"recSm6AXwe"}}]
  # extra = json.dumps({
  #     "bitablePerm": {
  #         "tableId": TABLE_ID, # 附件所在数据表 id
  #         "attachments": {
  #             FIELD_ID: { # 附件字段 id
  #                 RECORD_ID: [ # 附件所在记录 record_id
  #                     FILE_TOKEN # 附件 file_token
  #                 ]
  #             }
  #         }
  #     }
  # })
  FILE_TOKEN = "Cr5vbHYMWokUYyxseBfc395Jnqh"
  extra = json.dumps({
    "bitablePerm": {
      "tableId": "tblsbCJnrsLMNrms",
      "attachments": {
        "fldSP3jGD4": {
          "recu1wRe6gZulT": [
            FILE_TOKEN
          ]
        }
      }
    }
  })

  # 构造请求对象
  request = DownloadMediaRequest.builder() \
      .file_token(FILE_TOKEN) \
      .extra(extra) \
      .build()

  # 发起请求
  response = client.drive.v1.media.download(request)

  # 保存文件到本地
  DOWNLOAD_FILE_NAME = response.file_name
  f = open(f"{response.file_name}", "wb")
  f.write(response.file.read())
  f.close()

  remove_image_bg(DOWNLOAD_FILE_NAME) # res: output.png
  # ============

  # 文件上传test=====

  # # 构造请求对象
  file_name = 'output.png'
  path = os.path.abspath(file_name)
  file = open(path, "rb")
  request = UploadAllMediaRequest.builder() \
      .request_body(UploadAllMediaRequestBody.builder()
          .file_name(file_name)
          .parent_type("bitable_file")
          .parent_node(APP_TOKEN)
          .size(os.path.getsize(path))
          .file(file)
          .build()) \
      .build()

  # 发起请求
  response: UploadAllMediaResponse = client.drive.v1.media.upload_all(request)

  file_token = response.data.file_token
  print(file_token)

  # 构造请求对象
  request = UpdateAppTableRecordRequest.builder() \
      .table_id(TABLE_ID) \
      .record_id('rechm9t4PD') \
      .request_body(AppTableRecord.builder()
              .fields({
                  "附件": [{"file_token": file_token}] # 👆🏻前面接口返回的 file_token
              })
              .build()) \
      .build()

  response: UpdateAppTableRecordResponse = client.base.v1.app_table_record.update(
    request)
  # ==============

  # 2. obtain fields
  list_field_request = ListAppTableFieldRequest.builder() \
    .page_size(100) \
    .table_id(TABLE_ID) \
    .build()

  list_field_response = client.base.v1.app_table_field.list(list_field_request)
  fields = getattr(list_field_response.data, 'items') or []

  # 3. get Text fields
  text_field_names = [
    field.field_name for field in fields if field.ui_type == 'Text'
  ]

  # 4. iterate through all the records
  list_record_request = ListAppTableRecordRequest.builder() \
    .page_size(100) \
    .table_id(TABLE_ID) \
    .build()

  list_record_response = client.base.v1.app_table_record.list(
    list_record_request)
  records = getattr(list_record_response.data, 'items') or []

  records_need_update = []

  for record in records:
    record_id, fields = record.record_id, record.fields
    new_fields = {}

    for key, value in fields.items():
      # replace the value
      if key in text_field_names:
        new_value = value.replace(source, target)
        # add field into new_fields
        new_fields[key] = new_value if new_value != value else value

    if len(new_fields.keys()) > 0:
      records_need_update.append({
        "record_id": record_id,
        "fields": new_fields
      })

  print(records_need_update)

  # 5. batch update records
  batch_update_records_request = BatchUpdateAppTableRecordRequest().builder() \
    .table_id(TABLE_ID) \
    .request_body(
      BatchUpdateAppTableRecordRequestBody.builder() \
        .records(records_need_update) \
        .build()
    ) \
    .build()
  batch_update_records_response = client.base.v1.app_table_record.batch_update(
    batch_update_records_request)
  print('success!')


if __name__ == "__main__":
  # replace all 'abc' to '233333'
  search_and_replace_func('abc', '233333')
