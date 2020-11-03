from pyad import aduser, adgroup
from operator import itemgetter

class SortTeam():
    '''
    Class that sorts members of a team/group in AD.\n
    Methods:\n
    __init__(self, member) -> SortTeam\n
    get_list(self) -> list[aduser.ADUser]
    '''
    def __init__(self, members):
        '''
        Initalizes an instance or SortTeam with a list of members from a group from AD.\n
        Parameters:\n
        :members (list[aduser.ADUser]): List of the members in the group.\n
        __init__(self, members) -> SortTeam
        '''
        self.members = members
        self.sortable_list = self.__sortable__()
        self.sorted_list = []
        for e in self.sortable_list:
            for m in self.members:
                if e[0] == m.get_attribute('cn', False):
                    self.sorted_list.append(m)
        
    def __sortable__(self):
        '''
        Sortes the list in `self.members` by reversed group membershit and then by name.\n
        __sortable__(self) -> list[tuple(str, str)]
        '''
        members = self.members
        sortable_list = []
        for member in members:
            if type(member) == aduser.ADUser:
                sortable_list.append((member.get_attribute('cn', False), sorted(member.get_attribute('memberOf', True))))
        return sorted(sorted(sortable_list, key=itemgetter(0), reverse=False), key=itemgetter(1), reverse=True)

    def __cns__(list_dns=[]):
        '''
        Returns a string of cns from a users groupmemberships.\n
        Parameters:\n
        :list_dns (list[str]): `memberOf` attribute of the `aduser.ADUser` object\n
        __cns__(list_dns) -> str
        '''
        r = ""
        for dn in dns:
            g = adgroup.ADGroup.from_dn(str(dn))
            r += g.get_attribute('cn', False) + ","
        if r[-1] == ",":
            r = r[0:-1]
        return r

    def get_list(self):
        '''
        Returns the fully sorted list `self.sorted_list`\n
        get_list(`self`) -> list[aduser.ADUser]
        '''
        return self.sorted_list