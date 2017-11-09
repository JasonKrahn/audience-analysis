from pypbi.core import PowerBI
from aa_backend import util as u
if __name__ == '__main__':

    p = PowerBI(u.get_setting("powerbi", "user_name"),
                u.get_setting("powerbi", "password"),
                u.get_setting("powerbi", "client_id"))
    p.connect()

    print(list(p.get_workspaces()))