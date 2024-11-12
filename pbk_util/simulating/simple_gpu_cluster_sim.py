import random
import time

SUCCESS = 'Success!'
FAILURE = 'Failure!'


class FailureDomain:
    def __init__(self, name, failure_count, in_secs, sub_domains=None, verbose=False):
        self.name = name  # Name of the failure domain, e.g., "Region A", "Zone A", "Server 1" etc.
        self.failure_count = failure_count
        self.in_secs = in_secs
        self.sub_domains = sub_domains if sub_domains else list()
        self.verbose = verbose
        self.failure_rate_per_sec = self.failure_count / self.in_secs

    def get_failure_or_success(self, interval):
        fail_chance = random.random() < (self.failure_rate_per_sec * interval)
        if fail_chance:
            self_status = FAILURE
        else:
            self_status = SUCCESS

        sub_domain_status = [d.get_failure_or_success(interval) for d in self.sub_domains]

        if self.verbose:
            print(f'{self.name} - self_status: {self_status}')
        if self.sub_domains and self.verbose:
            print(f'{self.name} - sub_domain_status: {sub_domain_status}')

        if self_status == FAILURE or FAILURE in sub_domain_status:
            # if self_status == FAILURE:
            #     print(f'{time.time()} - {self.name} failed')
            # else:
            #     if self.verbose:
            #         print(f'{self.name} had sub-domain-failure')
            return FAILURE
        else:
            return SUCCESS


if __name__ == "__main__":
    seconds_in_year = 365*24*60*60
    gpu_failure_count = 268/16000
    gpu_failure_interval = 60*60*24*54

    server_annual_failure_count = 0.001
    num_servers = 2000
    num_gpus_per_server = 8

    cluster = FailureDomain(name=f"cluster", failure_count=0, in_secs=seconds_in_year)
    for s in range(num_servers):
        server = FailureDomain(f"{cluster.name}_Server_{s}", server_annual_failure_count, seconds_in_year)
        for i in range(num_gpus_per_server):
            gpu = FailureDomain(f"{server.name}_GPU_{i}", gpu_failure_count, gpu_failure_interval)
            server.sub_domains.append(gpu)

        cluster.sub_domains.append(server)

    print("Running simulation for 90 days...")
    num_failures = 0
    batches = int(90*24*60*60/120)
    start_time = time.time()
    last_fail_time = start_time
    last_fail_batch = 0
    for batch in range(batches):
        batch_status = cluster.get_failure_or_success(interval=120)
        if batch_status == FAILURE:
            num_failures += 1
            current_failure_time = time.time()
            hours_since_last_failure = (batch - last_fail_batch) * 120 / 60 / 60
            days_since_start = batch * 120 / 60 / 60 / 24

            print(f'{hours_since_last_failure*60:0.1f} Minutes since last failure. '
                  f'({days_since_start:0.1f} days) have passed. '
                  f'{num_failures / days_since_start:0.1f} Avg Failures per Day')

            last_fail_time = current_failure_time
            last_fail_batch = batch
