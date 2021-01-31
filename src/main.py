from speedtest import Speedtest
from datetime import datetime
from pandas import read_csv, DataFrame
from sched import scheduler
from time import time, sleep


class Tester:

    def __init__(self):
        self.speed_test = Speedtest()
        pass

    def ping(self) -> float:
        self.speed_test.get_best_server()
        return self.speed_test.results.ping

    def upload(self) -> float:
        upload = self.speed_test.upload()
        upload_mbs = round(upload / (10 ** 6), 2)
        return upload_mbs

    def download(self) -> float:
        download = self.speed_test.download()
        download_mbs = round(download / (10 ** 6), 2)
        return download_mbs


class Storage:

    def __init__(self, csv_file=None):
        self.index = "Time"
        self.header = ["Ping (ms)", "Download (Mb/s)", "Upload (Mb/s)"]
        if csv_file is None:
            self.csv_file_name = "internet_speeds_dataset.csv"
        else:
            self.csv_file_name = csv_file

    def load_data(self):
        # Load the CSV to update
        try:
            csv_dataset = read_csv(self.csv_file_name, index_col=self.index)
        # If there's an error, assume the file does not exist and create\
        # the dataset from scratch
        except:
            csv_dataset = DataFrame(
                list(),
                columns=["Ping (ms)", "Download (Mb/s)", "Upload (Mb/s)"]
            )
        return csv_dataset

    def store(self, idx: str, ping: float, download_speed: float, upload_speed: float):
        # Get today's date in the form Month/Day/Year
        csv_dataset = self.load_data()
        # Create a one-row DataFrame for the new test results
        results_df = DataFrame(
            [[ping, download_speed, upload_speed]],
            columns=self.header,
            index=[idx]
        )

        updated_df = csv_dataset.append(results_df, sort=False)
        # https://stackoverflow.com/a/34297689/9263761
        updated_df \
            .loc[~updated_df.index.duplicated(keep="last")] \
            .to_csv(self.csv_file_name, index_label=self.index)


def measure():
    now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print('%s: Starting measure' % now)
    ping_ms = tester.ping()
    download_mbs = tester.download()
    upload_mbs = tester.upload()
    storage.store(now, ping_ms, download_mbs, upload_mbs)
    print('%s: Measuring finished. Ping=[%s]ms, download=[%s]mb/s, upload=[%s]mb/s' %
          (datetime.today().strftime("%Y.%m.%d %H:%M:%S"), ping_ms, download_mbs, upload_mbs))
    sched.enter(120, 1, measure, ())


if __name__ == '__main__':
    tester = Tester()
    storage = Storage()

    sched = scheduler(time, sleep)
    sched.enter(1, 1, measure, ())
    sched.run()
