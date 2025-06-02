import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

import firebase
from config import BIGQUERY_DATASET_ID, BIGQUERY_TABLE_ID, credentials_dict

credentials = service_account.Credentials.from_service_account_info(credentials_dict)


@st.cache_resource()
def bq():
    client = bigquery.Client(credentials=credentials)
    return client


@st.cache_data(ttl=60 * 10)
def query(sql) -> pd.DataFrame:
    return bq().query(sql).to_dataframe()


def index():
    if not firebase.refresh_token():
        st.rerun()
        return

    st.subheader("Billing Data")
    sql = f"""
    SELECT
        service.description as service,
        sku.description as sku,
        cost,
        usage_start_time,
        usage_end_time
    FROM `{credentials_dict.get("project_id")}.
        {BIGQUERY_DATASET_ID}.{BIGQUERY_TABLE_ID}`
    LIMIT 10
    """
    st.dataframe(query(sql))


if "user" not in st.session_state:
    st.text("左のメニュー[home]からログインしてください。")
else:
    index()
