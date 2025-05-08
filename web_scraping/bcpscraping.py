from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd

website = "https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante"
path = 'C:/Users/Usuario/Downloads/chromedriver-win64/chromedriver.exe'

service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)
driver.get(website)

wait = WebDriverWait(driver, 10)


month_averages = []  # To store averages for each month
year = 2019
try:
    element = wait.until(EC.element_to_be_clickable((By.ID, "dp_cotizacion")))
    element.click()
    time.sleep(1)

    # Set year only once
    year_select = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker-year")))
    Select(year_select).select_by_visible_text(str(year))

    for month in range(0, 12):  # 0 to 11 for Jan to Dec
        monthly_values = []

        # Select the month
        month_select = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker-month")))
        Select(month_select).select_by_value(str(month))
        time.sleep(1.5)

        for fecha in range(1, 32):  # 2 to 31
            try:
                day_str = str(fecha)
                available_dates = driver.find_elements(By.XPATH, f'//td[@title="Available"]/a[text()="{day_str}"]')

                if not available_dates:
                    print(f"Month {month}, Date {day_str} not available — skipping.")
                    continue

                available_dates[0].click()

                cell_xpath = "/html/body/div[2]/div[3]/div/table/tbody/tr[59]/td[2]"
                wait.until(EC.presence_of_element_located((By.XPATH, cell_xpath)))  # Just wait
                value_str = driver.find_element(By.XPATH, cell_xpath).text.strip().replace(".", "").replace(",", ".")

                value = float(value_str)
                monthly_values.append(value)
                print(f"Month {month}, Date {day_str} — Value: {value}")
                time.sleep(1)

                # Reopen calendar after scraping value
                element = wait.until(EC.element_to_be_clickable((By.ID, "dp_cotizacion")))
                element.click()
                time.sleep(1)

            except (TimeoutException, NoSuchElementException, ElementNotInteractableException, ValueError) as e:
                print(f"Error on month {month}, date {fecha}: {e}")
                continue

        # End of month — calculate and store average
        if monthly_values:
            avg_value = sum(monthly_values) / len(monthly_values)
            month_averages.append({"Year": year, "Month": month+1, "AverageValue": avg_value})
            print(f"Month {month} average: {avg_value}")
        else:
            month_averages.append({"Month": month, "AverageValue": None})
            print(f"Month {month} had no available values.")

finally:
    driver.quit()

# Create DataFrame
df = pd.DataFrame(month_averages)
print(df)
df.to_csv("usdavg2019.csv", index=False)

