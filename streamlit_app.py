# Import necessary libraries

import streamlit as st
from requests import get
from bs4 import BeautifulSoup as bs
import pandas as pd
import io
import time
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt


################################## Set of function to handle scraping over  url 1 : https://dakar-auto.com/senegal/voitures-4 #############################

                            # <----------------- A function to get a container (car) data (information)   ------------------------------->
 

def get_car_info(car):
    """
        This function 'get_car_info' is design to take as parameter a bs4 object (a car container) and return the necessary informations about this one.
        Those informations are returned in tuple to avoid accidentel modification.
        
        Usage: get_car_info(car)
    """
    try:
     
        # scrape the car brand, model and the year
        general_information_1 = car.find('h2', 'listing-card__header__title mb-md-2 mb-0').a.text.strip().split()

        # get the brand
        brand = general_information_1[0]

        # get the year
        year= general_information_1[-1]

        # Scrape the reference, kilometer driven, fuel type and gearbox type
        general_information_2  = car.find_all('li', 'listing-card__attribute list-inline-item')


        # get kilometer driven
        kilometerage = general_information_2[1].text.replace(' km','').strip()

        # get fuel type
        fuel_type = general_information_2[3].text.strip()

        # get gearbox
        gearbox = general_information_2[2].text.strip()

        # scrape the price
        price = "".join(car.find('h3', "listing-card__header__price font-weight-bold text-uppercase mb-0").text.strip().split()).replace('FCFA', '')


        # get the address
        address = ''.join(car.find('div', 'col-12 entry-zone-address').text.strip().split('\n'))

        # get the woner

        owner  = ' '.join(car.find('p','time-author m-0').text.strip().split()[1::])

    except:
        pass
    
    return (brand,year,price,address,kilometerage,gearbox,fuel_type,owner)



                            # <----------------- A functions to get all cars informations on a page   ------------------------------->
                            
    
def get_all_cars(page_link):
    
    """
        This function is design to return a DataFrame of all car on a given page link. It take in parameter
        a link to a specific page.
        
        Usage: get_all_cars(page_link) 
    """
    
    # A list of the cars
    cars_list = []
    
    # A page content 
    respons = get(page_link)

    # stock the html in a beautifulsoup objet with a html parser (a parser allows to easily navigate through the html code)
    soup = bs(respons.content,'html.parser')

    # Get all cars
    containers = soup.find_all('div','listings-cards__list-item mb-md-3 mb-3')

    for car in containers:
        try:
            car_info = get_car_info(car)
            car_dic = {
                'Brand':car_info[0],
                'Year':car_info[1],
                'Price':car_info[2],
                'Address':car_info[3],
                'Kilometerage':car_info[4],
                'Gearbox':car_info[5],
                "Fuel":car_info[6],
                "Owner":car_info[7]
                }
            cars_list.append(car_dic)
        except:
            pass
    
    return pd.DataFrame(cars_list)
        

                            # <----------------- A function to get all page request by user   ------------------------------->


def get_all_cars_all_pages(page_number):
    
    """
        This function is a principal function use to get all car information aver multiple pages.
        It use the both precedent functions to achive its goal. All missing values and duplicates are drop.
        
        Usage: get_all_cars_all_pages(number_of_page)
    """
    
    df = pd.DataFrame()
    for i in range(1,page_number+1):
        url = f'https://dakar-auto.com/senegal/voitures-4?&page={i}'
        df = pd.concat([df,get_all_cars(url)],axis=0).reset_index(drop=True)
        df = df.drop_duplicates()
    return df

##############################################End of set of URL 1 Scraping functions #######################################################################









######################### Set of function to handle scraping over  url 2: https://dakar-auto.com/senegal/motos-and-scooters-3 #############################


                            # <----------------- A function to get a motor informations   ------------------------------->

                    
def get_motor_info(motor):
    
    """
    The function get_motor_info() is design to return the necessary information on a motor. It tahe in parameter a bs4 object (a container of a motor). Those informations are returned in tuple to avoid accidentel modification.
    
    Usage: get_motor_info(a_motor_soup)
    """
    try:
            #Get brand, model, year in general info
            gen_inf_1 = motor.find('h2','listing-card__header__title mb-md-2 mb-0').text.strip().split(' ')
          
            #get the brand
            brand = gen_inf_1[0]
          
            # get the year
            year = gen_inf_1[-1]
          
            # price
            price = ''.join(motor.find('h3','listing-card__header__price font-weight-bold text-uppercase mb-0').text.strip().replace(' F CFA','').split())

            # address
            address =' '.join(motor.find('div','col-12 entry-zone-address').text.strip().split('\n'))

            #kilometerage
            gen_inf_2 = motor.find_all('li','listing-card__attribute list-inline-item')
            if(len(gen_inf_2)>1): # to avoid error raised by motor that doesn't have driven km, the value will be Nan (missing value)
                kilometerage  = gen_inf_2[1].text.strip().split()[0]
            else:
                kilometerage = 0 # We define missing kilometerage value to 0

            # get the owner
            owner = ' '.join(motor.find('p','time-author m-0').text.strip().split(' ')[1::])
    except:
        pass
    
    return (brand,year,price,address,kilometerage,owner)
    



                            # <----------------- A function to get all motors on a page   ------------------------------->

def get_all_motors(page_link):
    
    """
        This function, get_all_motors() take in parameter alink of a specific page and return a dataframe of all motor present on this page. 
        It use the precedent function in a for loop.
    """
    response = get(page_link)
    soup = bs(response.content,'html.parser')
    motors = soup.find_all('div','listing-card__content__inner')
    
    motors_list = []
    
    for motor in motors:
        
        motor_info = get_motor_info(motor)
        motor_dic = {
            'Brand':motor_info[0],
            'Year':motor_info[1],
            'Price':motor_info[2],
            'Address':motor_info[3],
            'Kilometerage':motor_info[4],
            'Owner':motor_info[5]
        }
        motors_list.append(motor_dic)
        
    return pd.DataFrame(motors_list)


                            # <----------------- A function to get all motors a cros all pages requested by a user   ------------------------------->
                            
def get_all_motors_all_pages(page_number):
    
    """
        This function get_all_motors_all_pages() take in parameter the number of page upiwant to scrape 
        and return a DataFrame contain all motors across those pages. It use the two precedent functions. All missing values and duplicates are drop.
        Usage: get_all_motors_all_pages(3)
    """
    # An empty data frame to stock by adding the dataframes for each page
    all_motors_df = pd.DataFrame() 
         
    for page in range(1,page_number+1):
        
        # a full url with a spacific page number 
        url = f'https://dakar-auto.com/senegal/motos-and-scooters-3?&page={page}'
        
        response = get(url)
        soup = bs(response.content,'html.parser')
        motors = soup.find_all('div','listing-card__content__inner')
        all_motors_df = pd.concat([all_motors_df,get_all_motors(url)],axis=0).reset_index(drop=True)
        
    return all_motors_df.dropna().drop_duplicates()


##############################################End of set of URL 2 Scraping functions #######################################################################








######################### Set of function to handle scraping over  url 3: https://dakar-auto.com/senegal/location-de-voitures-19 #############################


                            # <----------------- A function to get an hire car informations   ------------------------------->


def get_hire_car_info(hire_car):
    
    """
    This function help to get the cessary information about a care to hire. It take in parameter a bs4 object, the container of a care. Those informations are returned in tuple to avoid accidentel modification.
    
    Usage: get_hire_car_info(hire_car_soup)
    """
    
    try:
        
        # get the brand
        brand = hire_car.find('h2','listing-card__header__title mb-md-2 mb-0').text.strip().split()[0]

        # get year
        year = hire_car.find('h2','listing-card__header__title mb-md-2 mb-0').text.strip().split()[-1]

        # get the price 
        price = "".join(hire_car.find('h3', "listing-card__header__price font-weight-bold text-uppercase mb-0").text.strip().split()).replace('FCFA', '')

        # get the address
        address = ''.join(hire_car.find('div', 'col-12 entry-zone-address').text.strip().split('\n'))

        # get the Owner
        owner  = ' '.join(hire_car.find('p','time-author m-0').text.strip().split()[1::])
                
    except:
        pass
    
    return (brand,year,price,address,owner)






                            # <----------------- A function to get all hire car on a page   ------------------------------->
                        
def get_all_hire_cars(page_link):
    
    
    """
        This function help you to get all hire car on a specific given page via the page link or url. It return a DataFrame contain all the informations.
        
        Usage: get_all_hire_cars(page_link)
    """
    
    # get the code 
    response = get(page_link)
            
    # store the code in a Beautifulsoup objet 
    soup = bs(response.content,'html.parser')

    # find the containers  (hiring car)
    hire_cars = soup.find_all("div","listing-card__content p-2")
    
    hire_car_list = []
    
    for hire_car in hire_cars:
        hire_car_info = get_hire_car_info(hire_car)
        
        hire_car_dic = {
            'Brand':hire_car_info[0],
            'Year':hire_car_info[1],
            'Price':hire_car_info[2],
            'Address':hire_car_info[3],
            'Owner':hire_car_info[4]
        }
        hire_car_list.append(hire_car_dic)
        
    return pd.DataFrame(hire_car_list)




                            # <----------------- A function to get all hire car cross all pages requested   ------------------------------->

def get_all_hire_cars_all_page(number_pages):
    
    """
        This function return all information about all hire car on the first number of page you given in parameter. All missing values and duplicates are drop.
        Usege: get_all_hire_cars_all_page(number_of_page)
    """
    
    # the base url
    base_url = 'https://dakar-auto.com/senegal/location-de-voitures-19?&page={}'
    
    # Data for all hire care
    hire_car_df = pd.DataFrame()
    
    for page in range(1,number_pages+1):
    
        url = base_url.format(page)  # buld a url for specic page
        tmp_df = get_all_hire_cars(url) # get the content of the page
        hire_car_df = pd.concat([hire_car_df,tmp_df],axis=0).reset_index(drop=True) #concat the information a page and the pasts pages
        hire_car_df = hire_car_df.dropna().drop_duplicates() # drop the missing values and the duplicated rows
    return hire_car_df


##############################################End of set of URL 3 Scraping functions #######################################################################


############################################## Function to save scraped data (with web scraper in sql db) #######################################################################

def save_in_db(data_state, csv_files):
    
    data_state = data_state.lower().strip()

    if data_state == "clean":
        db_name = "data/cleaned_data.db"
    else:
        db_name = "data/uncleaned_data.db"

    # nonexion to the corresponding data base
    conn = sqlite3.connect(db_name)

    try:
        for csv_path in csv_files:
            path_obj = Path(csv_path)

            # We take the cvs file name withou the extension as the corresponding table
            table_name = path_obj.stem  
            
            # reading of a csv file
            df = pd.read_csv(path_obj)

            # writing the dataframe read in the database
            df.to_sql(table_name, conn, if_exists="replace", index=False)

    finally:
        conn.close()
 
 
# This line was run once
#save_in_db("unclean",["Dakar_Auto_Hire_Auto.csv","Dakar_Auto_Sale.csv","Daka_Auto_Motors_Scooters.csv"])
  
############################################## Function to save scraped data (with web scraper in sql db) #######################################################################



# The web page general config, page title
st.set_page_config(page_title="Scraping App", layout="wide")



# A function de handle live sceaping according to the user choice. It call the specific function according to the choice from a user
def run_scraper(scrap_type, n_pages):
    if scrap_type == "Car for sale":
        return get_all_cars_all_pages(n_pages)
    elif scrap_type == "Motor for sale":
        return get_all_motors_all_pages(n_pages)
    elif scrap_type == "Car for hire":
        return get_all_hire_cars_all_page(n_pages)

#This function is used to converte a DataFrame object to csv and xlsx file for downloading
def convert_to_files(df):
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    xlsx_buffer = io.BytesIO()
    with pd.ExcelWriter(xlsx_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    xlsx_buffer.seek(0)

    return csv_bytes, xlsx_buffer


#  This table map the table in the databases with the display text for user choice. It help to know wich table content to load
TABLE_MAPPING = {
    "Car for sale": "Dakar_Auto_Sale",
    "Motor for sale": "Daka_Auto_Motors_Scooters",
    "Car for hire": "Dakar_Auto_Hire_Auto",
}

def load_unclean_table(data_type,db_path="data/uncleaned_data.db"):
    """
    This function help to load the corresponding table from SQLite DB, specificaly in from uncleaned_data.db. 
    It returns a DataFrame.
    """
    table_name = TABLE_MAPPING[data_type]
    
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
    finally:
        conn.close() # Close the connection after loading the data

    return df


def load_clean_table(data_type: str, db_path="data/cleaned_data.db"):
    """
    This function help to load the corresponding table from SQLite DB, specificaly in from cleaned_data.db. 
    It returns a DataFrame"""
    
    table_name = TABLE_MAPPING[data_type]
    
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
    finally:
        conn.close() # Close the connection after loading the data

    return df

# the blck of the side bar. It content all possible action that can be choose by the user
with st.sidebar:
    st.title("Menu")

    # Subblock of live data scraping
    with st.expander("Live Data Scraping", expanded=True):

        scrap_type = st.radio(
            "Select a Data Type to Scrape",
            ["Car for sale", "Motor for sale", "Car for hire"],
            key="scrape_type"
        )

        n_pages = st.number_input(
            "Number of pages",
            min_value=1,
            max_value=200,
            value=1,
            step=1,
            key="scrape_pages"
        )
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #28a745;
                color: white;
                border-radius: 8px;
                padding: 0.5em 1.2em;
                font-weight: 600;
                border: none;
            }
            div.stButton > button:hover {
                background-color: #218838;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)

        scrape_btn = st.button("Validate", key="scrape_btn")

    # This one is the subblock of the scraped data downloading
    with st.expander("Download Scraped Data", expanded=False):
        st.write(
            """Select a DataSet 
                (uncleaned data)"""
        )

        download_type = st.radio(
            "Dataset:",
            ["Car for sale", "Motor for sale", "Car for hire"],
            key="download_type"
        )

        download_btn = st.button("Load data", key="download_btn")

    # The sublock for dashboard view part
    with st.expander("View Data Dashboard", expanded=False):
        st.write(
            "Select a cleaned DataSet"
        )

        dashboard_type = st.radio(
            "Dataset:",
            ["Car for sale", "Motor for sale", "Car for hire"],
            key="dash_type"
        )

        show_dashboard = st.button("Show dashboard", key="dash_btn")



    # Subblock to display form of the app evaluation
    with st.expander("Evaluate The App", expanded=False):
        eval_choice = st.radio(
            "Choose an evaluation form:",
            ["Google Form", "Kobo form"],
            key="eval_choice"
        )
        eval_btn = st.button("Open selected form", key="eval_btn")



def show_data_source_table():
    df_sources = pd.DataFrame(DATA_SOURCE_MAP)
    st.markdown("Data source mapping")
    st.table(df_sources)
    

# A map to guide user on our app by selecting the right data source our dataset
DATA_SOURCE_MAP = [
    {
        "Dataset": "Car for sale",
        "Source URL": "https://dakar-auto.com/senegal/voitures-4"
    },
    {
        "Dataset": "Motor for sale",
        "Source URL": "https://dakar-auto.com/senegal/motos-and-scooters-3"
    },
    {
        "Dataset": "Car for hire",
        "Source URL": "https://dakar-auto.com/senegal/location-de-voitures-19"
    },
]



# The principal part to display data
st.markdown("<h1 style='text-align: center; color: white;'>Data Scraping App</h1>", unsafe_allow_html=True)

st.markdown("""
        This App help to scrape data and clean them from [Daka-Auto](https://dakar-auto.com/) website""")

# Action when a user selecte or click scrap button
if scrape_btn:
    st.subheader(f"Scraping: {scrap_type}")

    progress = st.progress(0)
    status = st.empty()

    status.info("Scraping is running...")

    # Fake progress bar for UX
    for pct in range(0, 100, 5):
        progress.progress(pct)
        time.sleep(0.1)

    try:
        df = run_scraper(scrap_type, int(n_pages))

        progress.progress(100)
        status.success("Operation Completed")

        st.write("##### Data table preview")
        st.dataframe(df, use_container_width=True)

        csv_bytes, xlsx_buffer = convert_to_files(df)

        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=f"{scrap_type.replace(' ', '_').lower()}.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download XLSX",
            data=xlsx_buffer,
            file_name=f"{scrap_type.replace(' ', '_').lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except:
        pass


# Download directly from scraped data
elif download_btn:
    st.write(f"Unclean data loaded from database: {download_type}")

    try:
        df = load_unclean_table(download_type)
    except:
        pass
    else:
        if df.empty:
            st.warning("The table is empty in the database.")
        else:
            st.write("##### Data table preview")
            st.dataframe(df, use_container_width=True)

            csv_bytes, xlsx_buffer = convert_to_files(df)

            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name=f"{download_type.replace(' ', '_').lower()}_download.csv",
                mime="text/csv"
            )

            st.download_button(
                "Download XLSX",
                data=xlsx_buffer,
                file_name=f"{download_type.replace(' ', '_').lower()}_download.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# data table dashboard
elif show_dashboard:
    st.subheader(f"Dashboard – {dashboard_type}")

    try:
        df = load_clean_table(dashboard_type)
    except:
        pass
    else:
        if df.empty:
            st.warning("The cleaned table is empty in the database.")
        else:
            #  converte the data type in to numeric to avoid erreor
            if "Price" in df.columns:
                df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

            if "Year" in df.columns:
                df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

            # st.write("### Data preview")
            # st.dataframe(df.head(20), use_container_width=True)

            # graph of the distribution by prce
            if "Price" in df.columns:
                price_series = df["Price"].dropna()

                if not price_series.empty:
                    fig1, ax1 = plt.subplots()
                    ax1.hist(price_series, bins=30)
                    ax1.set_title("Price distribution")
                    ax1.set_xlabel("Price")
                    ax1.set_ylabel("Count")
                    st.pyplot(fig1)
                else:
                    st.info("No valid price data available for the histogram.")

            # mean price of top ten brand
            if "Price" in df.columns and "Brand" in df.columns:
                brand_price = (
                    df.dropna(subset=["Price"])
                      .groupby("Brand")["Price"]
                      .mean()
                      .sort_values(ascending=False)
                      .head(10)
                )

                if not brand_price.empty:
                    fig2, ax2 = plt.subplots()
                    brand_price.plot(kind="bar", ax=ax2)
                    ax2.set_title("Average price by brand (Top 10)")
                    ax2.set_xlabel("Brand")
                    ax2.set_ylabel("Average price")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig2)
                else:
                    st.info("Not enough data to compute average price by brand.")

            # number of car by year
            if "Year" in df.columns:
                year_counts = (
                    df["Year"].dropna()
                      .astype(int)
                      .value_counts()
                      .sort_index()
                )

                if not year_counts.empty:
                    fig3, ax3 = plt.subplots()
                    year_counts.plot(kind="bar", ax=ax3)
                    ax3.set_title("Number of vehicles by year")
                    ax3.set_xlabel("Year")
                    ax3.set_ylabel("Count")
                    plt.xticks(rotation=45, ha="right")
                    st.pyplot(fig3)
                else:
                    st.info("No valid year data available to plot counts by year.")


# evaluation form
elif eval_btn:
    if eval_choice == "Google Form":
        st.subheader("App Evaluation form (Google Forms)")

        st.markdown(
            "[Open this form in a new tab]"
            "(https://docs.google.com/forms/d/e/1FAIpQLSfuOpE215IKGv9_dblMhAHUWbsksVSIm4Bxo8brheqWpJIDhA/viewform?usp=publish-editor)"
        )

        st.markdown(
            """
            <iframe 
                src="https://docs.google.com/forms/d/e/1FAIpQLSfuOpE215IKGv9_dblMhAHUWbsksVSIm4Bxo8brheqWpJIDhA/viewform?embedded=true" 
                width="100%" 
                height="700" 
                frameborder="0" 
                marginheight="0" 
                marginwidth="0">
            Loading…
            </iframe>
            """,
            unsafe_allow_html=True
        )

    else:
        st.subheader("App Evaluation Form (KoboToolbox)")

        st.markdown(
            "[Open this form in a new tab](https://ee.kobotoolbox.org/x/7sT3NBO8)"
        )

        st.markdown(
            """
            <iframe 
                src="https://ee.kobotoolbox.org/x/7sT3NBO8" 
                width="100%" 
                height="700" 
                frameborder="0" 
                marginheight="0" 
                marginwidth="0">
            Loading…
            </iframe>
            """,
            unsafe_allow_html=True
        )


# Maping table displaying by default
else:
    show_data_source_table()

