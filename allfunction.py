from datetime import datetime, timedelta,timezone

def get_renewal_period(datelist:datetime |None =None,Basicplan:str = "Noplan")->datetime:

    renewal_days:int=0
    if datelist is None: datelist =datetime.now(timezone.utc)
    if Basicplan.lower() == "basic":
        renewal_days = 28
    elif Basicplan.lower() == "pro":
        renewal_days = 6 * 28
    elif Basicplan.lower() == "ultra":
        renewal_days = 12 * 28
    elif Basicplan.lower() == "noplan":
        renewal_days =0

    renewal_date = datelist + timedelta(days=renewal_days)

    return  renewal_date

def check_subscription_status(renewal_date: datetime ) -> bool:

    current_date = datetime.now().replace(tzinfo=None)
    renewal_date = renewal_date.replace(tzinfo=None)
    return current_date < renewal_date
