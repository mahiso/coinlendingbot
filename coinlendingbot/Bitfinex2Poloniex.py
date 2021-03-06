'''
Converts Bitfinex to Poloniex Api returns
'''

import datetime
import pytz


class Bitfinex2Poloniex(object):
    all_currencies = []

    @staticmethod
    def convertTimestamp(timestamp):
        '''
        Converts unix timestamp
        '''
        dt = datetime.datetime.fromtimestamp(float(timestamp), pytz.utc)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def convertOpenLoanOffers(bfxOffers):
        '''
        Convert from "offers" to "returnOpenLoanOffers"
        '''
        plxOffers = {}
        for offer in bfxOffers:
            if offer['currency'] not in Bitfinex2Poloniex.all_currencies:
                continue
            if offer['currency'] not in plxOffers:
                plxOffers[offer['currency']] = []

            if offer['direction'] == 'lend' and float(offer['remaining_amount']) > 0:
                plxOffers[offer['currency']].append({
                    "id": offer['id'],
                    "rate": str(float(offer['rate'])/36500),
                    "amount": offer['remaining_amount'],
                    "duration": offer['period'],
                    "autoRenew": 0,
                    "date": Bitfinex2Poloniex.convertTimestamp(offer['timestamp'])
                })

        return plxOffers

    @staticmethod
    def convertActiveLoans(bfxOffers):
        '''
        Convert from "credits" to "returnActiveLoans"
        '''

        plxOffers = {}
        plxOffers['provided'] = []
        plxOffers['used'] = []
        for offer in bfxOffers:
            if offer['currency'] not in Bitfinex2Poloniex.all_currencies:
                continue
            plxOffers['provided'].append({
                "id": offer['id'],
                "currency": offer['currency'],
                "rate": str(float(offer['rate']) / 36500),
                "amount": offer['amount'],
                "duration": offer['period'],
                "autoRenew": 0,
                "date": Bitfinex2Poloniex.convertTimestamp(offer['timestamp'])
            })

        return plxOffers

    @staticmethod
    def convertLoanOrders(bfxLendbook):
        '''
        Converts from 'lendbook' to 'returnLoanOrders'
        '''

        plxOrders = {
            'offers': [],
            'demands': [],
            'update_time': bfxLendbook['update_time']
        }

        for bid in bfxLendbook['bids']:
            plxOrders['demands'].append({
                'rate': '{0:0.8f}'.format(float(bid['rate'])),
                'amount': bid['amount'],
                'rangeMin': '2',
                'rangeMax': bid['period']
            })

        for ask in bfxLendbook['asks']:
            plxOrders['offers'].append({
                'rate': '{0:0.8f}'.format(float(ask['rate'])),
                'amount': ask['amount'],
                'rangeMin': '2',
                'rangeMax': ask['period']
            })

        return plxOrders

    @staticmethod
    def convertAccountBalances(bfxBalances, account=''):
        '''
        Converts from 'balances' to 'returnAvailableAccountBalances'
        '''
        balances = {}

        accountMap = {
            'trading': 'margin',
            'deposit': 'lending',
            'exchange': 'exchange'
        }

        if (account == ''):
            balances = {'margin': {}, 'lending': {}, 'exchange': {}}
        else:
            balances[account] = {}

        for balance in bfxBalances:
            currency = balance['currency'].upper()
            if (balance['type'] == 'conversion') or (currency not in Bitfinex2Poloniex.all_currencies):
                continue
            if (account == '' or account == accountMap[balance['type']]) and float(balance['amount']) > 0:
                balances[account][currency] = balance['available']

        return balances

    @staticmethod
    def convertTicker(bfxTicker):
        '''
        Converts Bitfinex websocket ticker data to Poloniex format
        '''
        ticker = {}
        for t in bfxTicker:
            couple = "{}_{}".format(t[3:], t[:3])
            couple_reverse = "{}_{}".format(t[:3], t[3:])
            ticker[couple] = {
                "last": float(bfxTicker[t]['last_price']),
                "lowestAsk": float(bfxTicker[t]['ask']),
                "highestBid": float(bfxTicker[t]['bid']),
                "update_time": bfxTicker[t]['update_time']
            }
            ticker[couple_reverse] = {
                        "last": 1 / float(bfxTicker[t]['last_price']),
                        "lowestAsk": 1 / float(bfxTicker[t]['ask']),
                        "highestBid": 1 / float(bfxTicker[t]['bid']),
                        "update_time": bfxTicker[t]['update_time']
                }
        return ticker
