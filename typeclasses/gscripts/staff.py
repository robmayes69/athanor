from evennia.utils.ansi import ANSIString
from athanor.base.systems import AthanorSystem
from world.models import StaffCategory, StaffEntry
from athanor import AthException


class StaffSystem(AthanorSystem):
    key = 'staff'
    system_name = 'STAFF'
    load_order = 0
    settings_data = (
        ('email', 'Email to display for inquiries?', 'email', 'replace@this.org'),
        ('show_email', 'Display the staff email for inquiries?', 'boolean', False),
        ('category_color', 'Color for Category name headers.', 'color', 'y'),
    )
    start_delay = True
    run_interval = 60

    def category_create(self, session, category_name, category_order):
        if not session.ath['core'].is_developer():
            raise AthException("Permission denied!")
        new_name = self.valid['dbname'](session, category_name, thing_name="StaffCategory")
        if StaffCategory.objects.filter(key__iexact=new_name).first():
            raise AthException("A StaffCategory already uses that name!")
        new_order = self.valid['unsigned_integer'](session, category_order, thing_name="StaffCategory Order")
        if StaffCategory.objects.filter(order=new_order).first():
            raise AthException("A StaffCategory already uses that order!")
        new_cat = StaffCategory.objects.create(key=new_name, order=new_order)
        new_cat.save()
        self.alert("Created new StaffCategory: %s (%s)" % (new_cat, new_order), source=session)

    def category_find(self, session, category_search):
        if not category_search:
            raise AthException("Nothing entered to search for!")
        found = StaffCategory.objects.filter(key__iexact=category_search).first()
        if found:
            return found
        StaffCategory.objects.filter(key__istartswith=category_search).first()
        if found:
            return found
        raise AthException("Could not find StaffCategory '%s'" % category_search)

    def category_rename(self, session, category_search, category_name):
        if not session.ath['core'].is_developer():
            raise AthException("Permission denied!")
        cat = self.category_find(session, category_search)
        new_name = self.valid['dbname'](session, category_name, thing_name='StaffCategory Name')
        if StaffCategory.objects.filter(key__iexact=new_name).exclude(id=cat).first():
            raise AthException("That StaffCategory name is already in use!")
        self.alert("StaffCategory '%s' Renamed to: %s" % (cat, new_name), source=session)
        cat.key = new_name
        cat.save()

    def category_reorder(self, session, category_search, category_order):
        if not session.ath['core'].is_developer():
            raise AthException("Permission denied!")
        cat = self.category_find(session, category_search)
        new_order = self.valid['unsigned_integer'](session, category_order, thing_name="StaffCategory Order")
        if StaffCategory.objects.filter(order=new_order).first():
            raise AthException("A StaffCategory already uses that Order number!")
        self.alert("Changed StaffCategory '%s' Order from %s to: %s" % (cat, cat.order, new_order), source=session)
        cat.order = new_order
        cat.save()

    def staff_add(self, session, account_search, category_search):
        if not session.ath['core'].is_developer():
            raise AthException("Permission denied!")
        account = self.systems['account'].search(session, account_search)
        if StaffEntry.objects.filter(account=account).first():
            raise AthException("%s is already a Staff Member!" % account)
        cat = self.category_find(session, category_search)
        new_entry = StaffEntry.objects.create(account=account, category=cat)
        new_entry.save()
        self.alert("Added Account '%s' to StaffCategory '%s'" % (account, cat), source=session)

    def staff_remove(self, session, account_search):
        if not session.ath['core'].is_developer():
            raise AthException("Permission denied!")
        account = self.systems['account'].search(session, account_search)
        found_entry = StaffEntry.objects.filter(account=account).first()
        if not found_entry:
            raise AthException("%s is not a Staff Member!" % account)
        cat = found_entry.category
        found_entry.delete()
        self.alert("%s has been removed from Staff!" % account, source=session)

    def staff_category(self, session, account_search, category_search):
        if not session.ath['core'].is_developer():
            raise AthException("Permission denied!")
        account = self.systems['account'].search(session, account_search)
        found_entry = StaffEntry.objects.filter(account=account).first()
        if not found_entry:
            raise AthException("%s is not a Staff Member!" % account)
        old_cat = found_entry.category
        cat = self.category_find(session, category_search)
        found_entry.category = cat
        found_entry.save()
        self.alert("%s has been moved to StaffCategory '%s' from '%s" % (account, cat, old_cat), source=session)

    def staff_order(self, session, account_search, entry_order):
        if not session.ath['core'].is_developer():
            raise AthException("Permission denied!")
        account = self.systems['account'].search(session, account_search)
        found_entry = StaffEntry.objects.filter(account=account).first()
        if not found_entry:
            raise AthException("%s is not a Staff Member!" % account)
        old_order = found_entry.order
        new_order = self.valid['unsigned_integer'](session, entry_order, thing_name="StaffEntry Order")
        found_entry.order = new_order
        found_entry.save()
        self.alert("%s has been re-ordered within StaffCategory '%s' to Order '%s'" % (account, found_entry.category, new_order), source=session)

    def staff_notes(self, session, account_search, new_notes):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied!")
        account = self.systems['account'].search(session, account_search)
        found_entry = StaffEntry.objects.filter(account=account).first()
        if not found_entry:
            raise AthException("%s is not a Staff Member!" % account)
        old_notes = found_entry.notes
        found_entry.notes = str(new_notes)
        found_entry.save()
        self.alert("%s has new StaffEntry Notes: %s" % new_notes, source=session)

    def staff_duty(self, session, account_search, new_duty):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied!")
        account = self.systems['account'].search(session, account_search)
        found_entry = StaffEntry.objects.filter(account=account).first()
        if not found_entry:
            raise AthException("%s is not a Staff Member!" % account)
        old_duty = found_entry.duty
        found_entry.duty = str(new_duty)
        found_entry.save()
        self.alert("%s changed Duty status: %s" % new_duty, source=session)

    def staff_vacation(self, session, account_search, new_vacation):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied!")
        account = self.systems['account'].search(session, account_search)
        found_entry = StaffEntry.objects.filter(account=account).first()
        if not found_entry:
            raise AthException("%s is not a Staff Member!" % account)
        if new_vacation.lower() in ['off', 'None', '0', 'clear']:
            found_entry.vacation = None
            self.alert("%s is no longer on Staff Vacation!" % account, source=session)
        else:
            vacation_date = self.valid['datetime'](session, new_vacation)
            found_entry.vacation = vacation_date
            self.alert("%s shall be on Vacation until: %s" % vacation_date, source=session)
        found_entry.save()

    def render_stafflist(self, session):
        color = self['category_color']
        output = list()
        output.append(session.ath['render'].header("Staff List"))
        for cat in StaffCategory.objects.all().order_by('order'):
            rank_string = ANSIString('|%s%s|n' % (color, cat.key))
            output.append(rank_string.center(78))
            staffers = ", ".join(str(s) for s in cat.staffers.all().order_by('order')).center(78)
            output.append(staffers)
        output.append(session.ath['render'].footer())
        return "\n".join(str(line) for line in output)
