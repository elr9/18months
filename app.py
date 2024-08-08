import streamlit as st
import pandas as pd

# Function to determine the last receipt date based on the remaining inventory
def get_last_receipt_date(inventory_df, receipts_df):
    results = []
    for part in inventory_df['Item number'].unique():
        inventory_qty = inventory_df[inventory_df['Item number'] == part]['Physical inventory'].values[0]
        part_receipts = receipts_df[receipts_df['ItemId'] == part].sort_values(by='DateFinancial', ascending=False)
        
        remaining_qty = inventory_qty
        last_receipt_date = None
        incomplete_record = False
        for idx, row in part_receipts.iterrows():
            if remaining_qty > row['Qty']:
                remaining_qty -= row['Qty']
            else:
                last_receipt_date = row['DateFinancial'].strftime('%m/%d/%Y')
                break
        
        if remaining_qty > 0 and not last_receipt_date:
            last_receipt_date = part_receipts.iloc[-1]['DateFinancial'].strftime('%m/%d/%Y')
            results.append({'Part Number': part, 'Inventory Quantity': inventory_qty, 
                            'Last Receipt Date': f'incomplete records, last receipt previous to {last_receipt_date}'})
        else:
            results.append({'Part Number': part, 'Inventory Quantity': inventory_qty, 'Last Receipt Date': last_receipt_date})
    return results

# Streamlit app
st.title('Inventory Last Receipt Date Finder')

# File upload
inventory_file = st.file_uploader('Upload the Inventory File', type=['csv', 'xlsx'])
transactions_file = st.file_uploader('Upload the Transactions File', type=['csv', 'xlsx'])

if inventory_file and transactions_file:
    if inventory_file.name.endswith('csv'):
        inventory_df = pd.read_csv(inventory_file)
    else:
        inventory_df = pd.read_excel(inventory_file)
    
    if transactions_file.name.endswith('csv'):
        transactions_df = pd.read_csv(transactions_file)
    else:
        transactions_df = pd.read_excel(transactions_file)
    
    # Filter transactions by "Purchase order" in column "TransType1"
    transactions_df = transactions_df[transactions_df['TransType1'] == 'Purchase order']
    
    # Ensure the relevant columns are in the correct data types
    transactions_df['DateFinancial'] = pd.to_datetime(transactions_df['DateFinancial'])
    transactions_df['Qty'] = transactions_df['Qty'].str.replace(',', '').astype(float)
    
    # Calculate the last receipt date
    last_receipt_dates = get_last_receipt_date(inventory_df, transactions_df)
    
    # Display results
    st.write('## Last Receipt Dates Based on Inventory')
    result_df = pd.DataFrame(last_receipt_dates)
    st.write(result_df)
else:
    st.write('Please upload both the inventory and transactions files.')
