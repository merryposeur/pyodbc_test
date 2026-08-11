import pandas as pd
import pyodbc


client_id = "416281"
query_parameters = [client_id]
connection_string = "DSN=AWSLive-TMNC"
charges_query = """
                        SELECT v_client_name as "Client Name",
                        PATID as "Client ID",
                        DATEADD(mm, DATEDIFF(mm, 0, date_of_service),0) as "Month",
                        SUM(guarantor_liability) AS "Charges",
                        0 AS "Payments",
                        0 AS "Adjustments",
                        0 AS "Transfers"
                        FROM SYSTEM.billing_tx_charge_detail 
                        WHERE LEFT(v_program_of_visit_code, 3) IN ('627', '628', '705') 
                        AND GUARANTOR_ID IN ('9', '12', '5000') 
                        AND PATID IN (?) 
                        GROUP BY v_client_name, PATID, DATEADD(mm, DATEDIFF(mm, 0, date_of_service), 0)
                    """

payments_query = """
                        SELECT v_client_name as "Client Name",
                        PATID as "Client ID",
                        DATEADD(mm, DATEDIFF(mm, 0, date_of_service),0) as "Month", 
                        0 AS "Charges", 
                        SUM(payment_amount) AS "Payments",
                        0 AS "Adjustments",
                        0 AS "Transfers"
                        FROM SYSTEM.billing_pay_adj_history 
                        WHERE GUARANTOR_ID IN ('9', '12', '5000')
                        AND payment_type_code LIKE '1%' 
                        AND PATID IN (?) 
                        GROUP BY v_client_name, PATID, DATEADD(mm, DATEDIFF(mm, 0, date_of_receipt), 0)
                    """

adjustments_query = """
                        SELECT v_client_name as "Client Name",
                        PATID as "Client ID",
                        DATEADD(mm, DATEDIFF(mm, 0, date_of_service),0) as "Month", 
                        0 AS "Charges", 
                        0 AS "Payments",
                        SUM(payment_amount) AS "Adjustments",
                        0 AS "Transfers"
                        FROM SYSTEM.billing_pay_adj_history 
                        WHERE GUARANTOR_ID IN ('9', '12', '5000')
                        AND payment_type_code LIKE '7%' 
                        AND PATID IN (?) 
                        GROUP BY v_client_name, PATID, DATEADD(mm, DATEDIFF(mm, 0, date_of_service), 0)
                    """

transfers_query = """
                        SELECT v_client_name as "Client Name",
                        PATID as "Client ID",
                        DATEADD(mm, DATEDIFF(mm, 0, date_of_service),0) as "Month", 
                        0 AS "Charges", 
                        0 AS "Payments",
                        0 AS "Adjustments",
                        SUM(payment_amount) AS "Transfers"
                        FROM SYSTEM.billing_pay_adj_history 
                        WHERE GUARANTOR_ID IN ('9', '12', '5000')
                        AND payment_type_code LIKE '4%' 
                        AND PATID IN (?) 
                        GROUP BY v_client_name, PATID, DATEADD(mm, DATEDIFF(mm, 0, date_of_service), 0)
                    """


with pyodbc.connect(connection_string) as cnxn:

    cnxn.timeout = 0

    df_charges = pd.read_sql(charges_query, cnxn, params=query_parameters)
    df_payments = pd.read_sql(payments_query, cnxn, params=query_parameters)
    df_adjustments = pd.read_sql(adjustments_query, cnxn, params=query_parameters)
    df_transfers = pd.read_sql(transfers_query, cnxn, params=query_parameters)

    df_charges = df_charges[["Client Name", "Client ID", "Month", "Charges"]]
    df_payments = df_payments[["Client ID", "Month", "Payments"]]
    df_adjustments = df_adjustments[["Client ID", "Month", "Adjustments"]]
    df_transfers = df_transfers[["Client ID", "Month", "Transfers"]]


final_df = pd.merge(df_charges, df_payments, on=["Client ID", "Month"], how="outer")
final_df = pd.merge(final_df, df_adjustments, on=["Client ID", "Month"], how="outer")
final_df = pd.merge(final_df, df_transfers, on=["Client ID", "Month"], how="outer")

numeric_columns = ["Charges", "Payments", "Adjustments", "Transfers"]
final_df[numeric_columns] = final_df[numeric_columns].fillna(0.0)

final_df["Client Name"] = final_df["Client Name"].bfill().ffill()

final_df = final_df.sort_values(by="Month").reset_index(drop=True)

final_df.to_csv("test_python_query.csv", index=False)
