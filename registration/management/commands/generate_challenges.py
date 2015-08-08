import sys, csv, re
from unidecode import unidecode

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from optparse import make_option
from registration.models import Registration, Challenge


try:
    from encrypter import encrypt
except Exception, e:
    print e
    sys.exit("Error: Must add encryption function.")

def get_word():
    return get_sentence().split(' ')[0]

class Command(BaseCommand):
    args = 'inputCsv [--reset]'
    help = 'Create challenges using csv input'

    option_list = BaseCommand.option_list + (
        make_option('--reset',
            action='store_true',
            dest='reset',
            default=False,
            help='Delete all challenges before generating new ones.'),
        )

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Usage: {0}'.format(self.args))

        if options['reset']:
            challenges = Challenge.objects.all()
            self.stdout.write('Deleting {0} challenges'.format(challenges.count()))
            for c in challenges:
                registrations_with_solved_challenge = Registration.objects.filter(solved_challenge=c)
                if registrations_with_solved_challenge.exists():
                    for r in registrations_with_solved_challenge:
                        self.stdout.write(
                            'Removing solved challenge %s from registration %s' % (
                                c, r))
                        r.solved_challenge = None
                        r.has_solved_challenge = False
                        r.save()
            challenges.delete()

        csv_filename = args[0]
        data = []
        try:
            with open(csv_filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except IOError, e:
            sys.exit("Error: File %s does not exist" % (csv_filename))

        created, ignored, failed = self.generate_challenges_from_csv(data)
        if created:
            self.stdout.write('Successfully generated {0} challenges'.format(created))
        if ignored:
            self.stdout.write('Ignored {0} challenges'.format(ignored))
        if failed:
            self.stdout.write('Failed to generate {0} challenges'.format(failed))

    def clean_message(self, m):
        return Challenge.clean_message(m)

    def generate_challenges_from_csv(self, data, **kwargs):
        obj_data = []
        for d in data:
            message = self.clean_message(d['Message'])
            if not message:
                continue

            obj_data.append({
                'language': d['Language'][:2].lower(),
                'decrypted_message': message,
                'encrypted_message': encrypt(message),
                'solved': False
            })

        created = 0
        ignored = 0
        failed = 0
        for d in obj_data:
            try:
                Challenge.objects.create(**d)
                created += 1
            except IntegrityError, e:
                self.stdout.write(
                    'Warning: "%(decrypted_message)s..." already exists in challenge database. '
                    'It will be ignored.' % {
                        'decrypted_message': d['decrypted_message'][:20]
                    }
                )
                ignored += 1
            except Exception, e:
                print 'Warning: ', str(e)
                failed += 1

        # # add challenge to one registration
        # c = Challenge.objects.first()
        # r = Registration.objects.first()
        # r.solved_challenge = c
        # r.has_solved_challenge = True
        # r.save()
        # c.solved = True
        # c.save()
        return (created, ignored, failed)








