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

    def __init__(self, index: str, header: [], csv_file: str):
        self.index = index
        self.header = header
        self.csv_file_name = csv_file

    def load(self) -> DataFrame:
        # Load the CSV to update
        try:
            csv_dataset = read_csv(self.csv_file_name, index_col=self.index)
        # If there's an error, assume the file does not exist and create\
        # the dataset from scratch
        except:
            csv_dataset = DataFrame(
                list(),
                columns=self.header
            )
        return csv_dataset

    def store(self, index: str, row: []):
        # Get today's date in the form Month/Day/Year
        csv_dataset = self.load()
        # Create a one-row DataFrame for the new test results
        results_df = DataFrame(
            [row],
            columns=self.header,
            index=[index]
        )

        updated_df = csv_dataset.append(results_df, sort=False)
        # https://stackoverflow.com/a/34297689/9263761
        updated_df \
            .loc[~updated_df.index.duplicated(keep="last")] \
            .to_csv(self.csv_file_name, index_label=self.index)


class PingStorage(Storage):

    def __init__(self):
        super().__init__("Time", ["Ping (ms)"], "internet_pings_dataset.csv")


class SpeedStorage(Storage):

    def __init__(self):
        super().__init__("Time", ["Ping (ms)", "Download (Mb/s)", "Upload (Mb/s)"], "internet_speeds_dataset.csv")


def ping_test():
    now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print('%s: Starting ping test' % now)
    ping_ms = tester.ping()
    pings.store(now, [ping_ms])
    print('%s: Ping test finished. Ping=[%s]ms' % (datetime.today().strftime("%Y.%m.%d %H:%M:%S"), ping_ms))
    sched.enter(20, 1, ping_test, ())


def speed_test():
    now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print('%s: Starting speed test' % now)
    ping_ms = tester.ping()
    download_mbs = tester.download()
    upload_mbs = tester.upload()
    speeds.store(now, [ping_ms, download_mbs, upload_mbs])
    print('%s: Speed test finished. Ping=[%s]ms, download=[%s]mb/s, upload=[%s]mb/s' %
          (datetime.today().strftime("%Y.%m.%d %H:%M:%S"), ping_ms, download_mbs, upload_mbs))
    sched.enter(120, 2, speed_test, ())


if __name__ == '__main__':
    tester = Tester()
    pings = PingStorage()
    speeds = SpeedStorage()

    sched = scheduler(time, sleep)
    sched.enter(1, 1, ping_test, ())
    sched.enter(10, 2, speed_test, ())
    sched.run()
