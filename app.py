from flask import Flask, render_template, request, redirect, url_for, jsonify , session, send_from_directory
import pandas as pd
import os
from werkzeug.utils import secure_filename
import shutil
import plotly.graph_objects as go
import json

if not os.path.exists('uploads'):
    os.makedirs('uploads')
app = Flask(__name__, static_url_path='/static')

column_names = []
files = []
file_path = []

UPLOAD_FOLDER = 'uploads'  # Create a directory to store the uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to generate column headers
def generate_headers(num_columns):
    headers = []
    current_column = 1
    while current_column <= num_columns:
        header = ""
        quotient = current_column
        while quotient > 0:
            remainder = (quotient - 1) % 26
            header = chr(65 + remainder) + header
            quotient = (quotient - 1) // 26
        headers.append(header)
        current_column += 1
    return headers

# Function to extract headers from Excel file
def extract_headers(file_path, sheet_name):
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Extract the number of columns
    num_columns = df.shape[1]

    # Generate column headers
    headers = generate_headers(num_columns)

    return headers


# Function to clear the uploads folder
def clear_uploads_folder():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

# Route to display the dashboard
@app.route('/')
def index():
    return render_template('index.html')


# Route to handle file upload and processing
@app.route('/upload', methods=['POST'])
def upload():
    
    global files, column_names

    files = request.files.getlist('data[]')
    column_names = []

    for file in files:
       
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(file_path)

        if file_path.endswith('.xls'):  # Check if the file is an Excel file
            df = pd.read_excel(file_path)
            column_names.extend(df.columns.to_list())

    # Generate column headers
    column_names = generate_headers(len(column_names))

    print(request.form.getlist('selectedMValues[]'))
    print([int(value) if value else 0 for value in request.form.getlist('from')])
    print([int(value) if value else 0 for value in request.form.getlist('to')])
    print(request.form.getlist('colh'))
    print([int(value) if value else 0 for value in request.form.getlist('rowc')])

    return {'columns': column_names, 'message': 'Files uploaded successfully!'}




def process_selected_values(selected_values, from_value, to_value, col_value, row_value, data = None):
    # data = request.get_json()
    # selected_values = data.get('selectedValues')
    # from_value = int(data.get('from'))
    # to_value = int(data.get('to'))

    # if data:
    #     from_values = [int(value) if value else 0 for value in data.getlist('from')]
    #     to_values = [int(value) if value else 0 for value in data.getlist('to')]
    # else:
    #     from_values = [from_value] * len(selected_values)
    #     to_values = [to_value] * len(selected_values) 

    col_value = col_value.split(',') #list(col_value)
    row_value = row_value.split(',')#list(row_value)
    row_value = [int(x) for x in row_value]
    # Subtract 2 from each value in row_value
    row_value = [x - 2 for x in row_value]
    # To check whether it is empty
    print(selected_values, from_value, to_value)# col_value, row_value)
    
    # Initialize an empty list to store the values
    result_list = []


    # Save the selected data to a new CSV file
    selected_data = pd.DataFrame()
    select_columns = selected_values
    start = from_value - 2
    end = to_value -1


    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        df = pd.read_excel(file_path)
        df.columns = generate_headers(len(df.columns))
        # Loop through each column and row specified
        for col, row in zip(col_value, row_value):
            value = df.at[row, col]
            result_list.append(value)
    
        output_list = []
        for item in result_list:
            if item not in output_list:
                output_list.append(item)

    print(output_list)

    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        df = pd.read_excel(file_path)
        df.columns = generate_headers(len(df.columns))
        df = df[select_columns].iloc[start:end]
        selected_data = pd.concat([selected_data,df])
    
    selected_data.columns = output_list
    selected_data_filename = 'selected_data.csv'
    selected_data.to_csv(selected_data_filename, index=False)
    
    # Read and print the contents of the selected_data.csv file
    try:
        df_selected_data = pd.read_csv(selected_data_filename)
        if not df_selected_data.empty:
            print(df_selected_data)
        else:
            print("The selected_data.csv file is empty.")
    except pd.errors.EmptyDataError:
        print("The selected_data.csv file is empty or does not contain any columns.")
    

    # Convert the dataset into a DataFrame (replace 'data' with your actual DataFrame)
    df = pd.DataFrame(selected_data)

# Create a separate line graph for each column
    graphs = []
    for column in df.columns :
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df[column], mode='lines', name=column, line=dict(color='blue')))
        # fig.add_trace(go.Scatter(y=df[column].iloc[from_values[i]: to_values[i]], mode='lines', name=column, line=dict(color='blue')))

    # Customize the plot
        fig.update_layout(title=f'Line Graph for {column}',
                      xaxis_title='X-axis Label (Data Point Index)',
                      yaxis_title='Y-axis Label',
                      showlegend=True,
                      margin=dict(l=50, r=20, t=70, b=50),
                      font=dict(family="Arial, monospace", size=12, color="#000000"),  # Change font color to black
                      plot_bgcolor="white",  # Set plot background color to white
                      paper_bgcolor="white",  # Set paper background color to white
                      xaxis=dict(showline=True, linewidth=1, linecolor="#BCCCDC", mirror=True),
                      yaxis=dict(showline=True, linewidth=1, linecolor="#BCCCDC", mirror=True),
                      autosize=True,
                      )

    # Display the plot
        # fig.show()
        graphs.append(fig.to_json())


    # return jsonify({'message': 'Selected values processed successfully!', 'filename': selected_data_filename})
    return {'graph':graphs}


selected_values_list = []
from_value_list = []
to_value_list = []
row_value_list = []
col_value_list =[]

def process_selected_multiple_values(files, selected_values_list, from_value_list, to_value_list, col_value_list, row_value_list):
    selected_values = request.form.getlist('selectedMValues[]')
    from_values = [int(value) if value else 0 for value in request.form.getlist('from')]
    to_values = [int(value) if value else 0 for value in request.form.getlist('to')]
    col_values = request.form.getlist('colh')
    row_values = [int(value) if value else 0 for value in request.form.getlist('rowc')]

   
    
    # Clear the lists
    selected_values_list.clear()
    from_value_list.clear()
    to_value_list.clear()
    row_value_list.clear()
    col_value_list.clear()

    # Save the values in the respective lists
    selected_values_list.extend(selected_values)
    from_value_list.extend(from_values)
    to_value_list.extend(to_values)
    row_value_list.extend(col_values)
    col_value_list.extend(row_values)

    

     # process_selected_values(selected_values, min(from_values), max(to_values))
    row_values = [int(x) for x in row_values]
    # Subtract 2 from each value in row_value
    row_values = [x - 2 for x in row_values]

    print(selected_values_list, from_value_list, to_value_list, row_value_list, col_value_list)

    # Initialize an empty list to store the values
    result_list = []

    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        df = pd.read_excel(file_path)
        df.columns = generate_headers(len(df.columns))
        # Loop through each column and row specified
        for col, row in zip(col_values, row_values):
            value = df.at[row, col]
            result_list.append(value)
    
        output_list = []
        for item in result_list:
            if item not in output_list:
                output_list.append(item)

    print(output_list)


    # Save the selected data to a new CSV file
    df1 = pd.DataFrame()
    select_columns = selected_values_list
    select_rows_from = from_value_list 
    select_rows_to= to_value_list 
    output_csv_file = "selected_data.csv"
    df1 = None
    select_rows_from = [x - 2 for x in select_rows_from]
    select_rows_to = [x - 2 for x in select_rows_to]

    graphs = []
    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        df = pd.read_excel(file_path)
        df.columns = generate_headers(len(df.columns))
        print(file)
        selected_data = []

        for col, start_row, end_row in zip(select_columns, select_rows_from, select_rows_to):
            data = df[col].iloc[start_row:end_row + 1].values
            selected_data.append(data.tolist())

        df_selection = pd.DataFrame(selected_data).T

        if df1 is None:
            df1 = df_selection
        else:
            df1 = pd.concat([df1, df_selection], axis=0)

    # Assign the column names
    df1.columns = output_list

    df1.reset_index(drop=True, inplace=True)

    # Save the DataFrame to CSV with header=True to include the column names
    # df1.to_csv(output_csv_file, index=False, header=True)

    # Step 1: Create a copy of the DataFrame
    result_df = df1.copy()

    # Step 2: Loop through each column and rearrange the NaN values
    for col in df1.columns:
        nan_mask = result_df[col].isna()
        non_nan_values = result_df[col][~nan_mask]
        nan_values = result_df[col][nan_mask]
        result_df[col] = pd.concat([non_nan_values, nan_values], ignore_index=True)

    # Display the final result
    # print(result_df)

    result_df.to_csv(output_csv_file, index=False, header=True)

    # Convert the dataset into a DataFrame 
    df = pd.read_csv("selected_data.csv")
    print(df)
    # Create a separate line graph for each colum
    for column in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df[column], mode='lines', name=column))

        # Customize the plot
        fig.update_layout(
            title=f'Line Graph for {column}',
            xaxis_title='X-axis Label (Data Point Index)',
            yaxis_title='Y-axis Label',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=20, t=70, b=50),
            font=dict(family="Arial, monospace", size=12, color="#424242"),
            plot_bgcolor="#f8f9fa",
            paper_bgcolor="#f8f9fa",
            xaxis=dict(showline=True, linewidth=1, linecolor="#BCCCDC", mirror=True),
            yaxis=dict(showline=True, linewidth=1, linecolor="#BCCCDC", mirror=True),
            autosize=True,
        )

    
    
        graphs.append(fig.to_json())

    return {'graph':graphs}

    # return jsonify({'message': 'Multiple values processed successfully!'})

@app.route('/process_selected_values', methods=['POST'])
def process_selected():
    if request.method == 'POST':
        if 'selectedMValues[]' in request.form:  # Processing multiple selected values
            selected_values = request.form.getlist('selectedMValues[]')
            from_values = [int(value) if value else 0 for value in request.form.getlist('from')]
            to_values = [int(value) if value else 0 for value in request.form.getlist('to')]
            col_values = request.form.getlist('colh')
            row_values = [int(value) if value else 0 for value in request.form.getlist('rowc')]
            print(selected_values)
            # return process_selected_values(selected_values, min(from_values), max(to_values),'','',request.form)
            return process_selected_multiple_values(files, selected_values_list, from_value_list, to_value_list, col_value_list, row_value_list)
        

        elif 'selectedValues' in request.json:  # Processing single selected values
            data = request.get_json()
            selected_values = data.get('selectedValues')
            from_value = int(data.get('from'))
            to_value = int(data.get('to'))
            col_value = str(data.get('colValue'))
            row_value = str(data.get('rowValue'))
            selected_columns = []
            selected_rows = pd.DataFrame()
            
            return process_selected_values(selected_values, from_value, to_value, col_value, row_value)
    
    return "selected_data.csv"



# Route to retrieve the list of columns
@app.route('/get_column_list', methods=['GET'])
def get_column_list():
    cols_lst = []
    for file in files:
        tmp = pd.read_csv(file.filename.split('/')[-1])
        cols_lst += list(tmp.columns)
    cols = list(set(cols_lst))
    data = {"columns": cols}
    return data
# Route to trigger the download of selected data
@app.route('/download_selected_data', methods=['GET'])
def download_selected_data():
    selected_data_filename = 'selected_data.csv'
    # clear_uploads_folder()
    return send_from_directory(".", selected_data_filename, as_attachment=True)

# Route to clear the uploads folder
@app.route('/clear_uploads', methods=['GET'])
def clear_uploads():
    clear_uploads_folder()
    return "Uploads folder cleared."



if __name__ == '__main__':
    app.run(debug=True)