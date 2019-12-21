#static
STC_MIN_LEN_USERNAME = 8
STC_TOKEN_EXPIRY_DATE = 30
STC_DEFAUL_PROFILE_IMG = ''

# messages
MSG_USER_NOT_EMPTY  = 'Users must have a username.'
MSG_EMAIL_NOT_EMPTY = 'Email must not be empty'
MSG_EMAIL_INVALID   = 'Email is invalid'
MSG_USERNAME_SHORT  = f'Username must have more than {STC_MIN_LEN_USERNAME} characters'
MSG_PROF_NOT_EXISTS = 'The requested profile does not exist.'

# choices
DEFAULT_DS_STATUS = 0
CHOICES_DS_STATUS = (
    (0, 'Available'),
    (1, 'Pending'),
    (2, 'Error')
)

USER_SUBSCRIPTION = (
    ('F', 'Free'),
    ('P', 'Premium'),
    ('E', 'Enterprise')
)
