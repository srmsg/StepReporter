import csv
import datetime
import logging
import sys
import time
import traceback

# Global variables
STEPUP_DAILY_REPORT_FILE = ''
FINAL_REPORT_FILE = ''
COMMITMENT_FILE = "commitment.csv"
REPORT_COLUMN_NAMES = ['Name', 'Total Steps', 'Pending Steps', 'Consistency Score', 'Consistency Target Achieved']
reportdata = []
CONSIST_MIN_AVG = {
    "60000": "8000",
    "70000": "9000",
    "80000": "10000",
    "90000": "11000",
    "100000": "12000",
    "110000": "15000"
}


def get_date_range():
    today = datetime.date.today()
    day_of_week = today.weekday()
    sunday_offset = day_of_week + 1
    start_date = today - datetime.timedelta(days=sunday_offset)

    dates = []
    for i in range((today - start_date).days):
        dates.append(start_date + datetime.timedelta(days=i))

    return dates


def get_commitment(name, commitments):
    for row in commitments:
        handle = f"{row.get('Name').strip(';')}"
        commitment = f"{row.get('commitment').strip(';')}"
        if (handle == name):
            return int(commitment)


# Main
date_range = get_date_range()
STEPUP_DAILY_REPORT_FILE = sys.argv[1]

print(STEPUP_DAILY_REPORT_FILE)
input_file = csv.DictReader(open(STEPUP_DAILY_REPORT_FILE))
reportdata.append(REPORT_COLUMN_NAMES)
for row in input_file:
    commitments = csv.DictReader(open(COMMITMENT_FILE))
    commitment_achieved = "N"
    commitment_achieved_count = 0
    name = f"{row.get('Name').strip(';')}"
    total_steps = f"{row.get('Total Steps').strip(';')};"
    avg_daily_steps = f"{row.get('Avg Daily Steps').strip(';')};"

    try:
        my_commitment = get_commitment(name, commitments)
        pending_steps = my_commitment - int(total_steps.strip(';'))
        if (pending_steps <= 0):
            pending_steps = 0
        seven_days_average = my_commitment / 7
        commitment_average = CONSIST_MIN_AVG[str(my_commitment)]

        for i in range(0, len(date_range)):
            formatted_date = date_range[i].strftime("%Y-%m-%d")
            dateValue = f"{row.get(formatted_date)};"
            if "N.A" in dateValue:
                dateValue = 0
                steps = 0
            else:
                steps = float(dateValue.strip(';'))
            if (steps >= (int(commitment_average))):
                commitment_achieved_count += 1
        if (commitment_achieved_count >= 5):
            commitment_achieved = "Y"
        print(name + "," + total_steps.strip(';') + "," + str(pending_steps) + "," + str(
            commitment_achieved_count) + "," + commitment_achieved)
        reportRow = [name, total_steps.strip(';'), str(pending_steps), str(commitment_achieved_count),
                     commitment_achieved]
        reportdata.append(reportRow)
    except Exception as e:
        logging.error(traceback.format_exc())
FINAL_REPORT_FILE = "report_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
with open(FINAL_REPORT_FILE, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(reportdata)
print("Report written to file --" + FINAL_REPORT_FILE)
