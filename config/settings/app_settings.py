USER_SETTINGS = {
    'any': {
        'minimum_sender_balance': 5,
        'minimum_withdrawal_amount': 25,
        'minimum_transfer_amount': 25,
        'referral_bonus': 5,
        'referral_work_commissions': 5,
        'activation_cost': 30,
    },

    'free': {
        'min_daily_video': 5
    },

    'paid': {
        'min_daily_video': 20,
        'validity_of_days': 90
    },

    'cron': {
        'task_cron_duration': 24 * 60 * 60,
        'task_cron_start_time': '0:0'
    },

    'admin': {
        'wallet': {
            'main': {
                'min_balance': 5
            },
            'referrer': {
                'min_balance': 0
            },
            'transfer': {
                'min_balance': 5
            }
        },
        'withdraw_request': {
            'min_active_refer_user': 1,
            'fees_in_percentage': 1
        }
    },

    'regional_admin': {
        'wallet': {
            'main': {
                'min_balance': 5
            },
            'referrer': {
                'min_balance': 5
            },
        },
        'withdraw_request': {
            'min_active_refer_user': 1,
            'fees_in_percentage': 1
        }
    }
}
