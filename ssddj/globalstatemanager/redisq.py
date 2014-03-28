import logging
from rq import use_connection
from rq_scheduler import Scheduler
from datetime import datetime
logger = logging.getLogger(__name__)
class SchedulerQ:
    def __init__(self):
        logger.info("Periodic command scheduler initialized")
        use_connection() # Use RQ's default Redis connection
        self.scheduler = Scheduler() # Get a scheduler for the "default" queue

def pp(str):
    print str

if __name__=="__main__":
    sq = SchedulerQ()
    sq.scheduler.schedule(
        scheduled_time=datetime.now(), # Time for first execution
        func=pp,                     # Function to be queued
        args=["Testing the scheduler"],             # Arguments passed into function when executed
        interval=60,                   # Time before the function is called again, in seconds
         repeat=10                      # Repeat this number of times (None means repeat forever)
    )

