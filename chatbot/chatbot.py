import requests
import configparser
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from fugle_realtime import intraday
from storeuserid import userdata

config = configparser.ConfigParser()
config.read('config.ini')
access_token = config['TELEGRAM']['ACCESS_TOKEN']
webhook_url = config['TELEGRAM']['WEBHOOK_URL']
api_token = config['TELEGRAM']['api_token']

requests.post('https://api.telegram.org/bot'+access_token+'/deleteWebhook').text
requests.post('https://api.telegram.org/bot'+access_token+'/setWebhook?url='+webhook_url+'/hook').text




# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=config['TELEGRAM']['ACCESS_TOKEN'])
@app.route('/hook', methods=['POST']) 
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'
    
#開始要先輸入id，如果已經輸入過就不用再輸入
def start(bot, update):
    if update.message.chat.id not in userdata().df.keys():
        bot.send_message(update.message.chat.id, '{} 您好，請輸入id：'.format(update.message.from_user.first_name)+'\n'+'(假設ID為 1111，請輸入：id1111)')
    else:
        bot.send_message(update.message.chat.id, '{} 您好，用戶ID:{}，請輸入欲查詢的股票代碼：'.format(update.message.from_user.first_name, userdata().df[update.message.chat.id]))
    
def info(bot, update):
    global num
    num = update.message.text #收到的訊息
    data = intraday.meta(apiToken=api_token , symbolId=num ,output='raw')
    
    '''對話框按鈕'''
    global reply_markup
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton('基本資訊', callback_data='info'),
        InlineKeyboardButton('最新一筆交易', callback_data='trade'),]])
    
    '''輸入id，且判斷id是否存在'''
    if 'id' in num:
        if int(num[2:]) not in  userdata().df['userid']:
            update.message.reply_text('ID%s 不存在'%(num[2:]))
        else:
            update.message.reply_text('登入成功 ID：%s，請輸入欲查詢的股票代碼：'%(num[2:]))
            userdata().write(update.message.chat.id,num[2:])
                   
    elif 'error' in intraday.chart(apiToken=api_token , symbolId='2330').columns:
        '''直接輸入股票代碼''' 
        update.message.reply_text('請輸入正確的股票代碼：')
    else:    
        df1 = intraday.chart(apiToken=api_token , symbolId=num)
        df1 = df1.iloc[-1]
        text = ('●'+data['nameZhTw']+num+'\t\t\t'+'股價：'+str(df1['close']))
#         update.message.reply_text(text,reply_markup = reply_markup)
        bot.send_message(update.message.chat.id, text+'\n\n'+'{} 您還可以查詢：'.format(update.message.from_user.first_name) 
                     , reply_to_message_id = update.message.message_id,reply_markup = reply_markup)
    

            
'''按鈕callback'''
def getClickButtonData(bot, update):
    data = intraday.meta(apiToken=api_token , symbolId=num ,output='raw')

    if update.callback_query.data == 'info':
        if 'industryZhTw' in data:
            text = ('產業別：'+data['industryZhTw']+'\n'+'交易幣別：'+data['currency']+'\n'+'股票中文簡稱：'+data['nameZhTw']+'\n'+'開盤參考價：'+ str(data['priceReference'])+'\n'+
                '漲停價：'+str(data[ 'priceHighLimit'])+'\n'+'跌停價：'+str(data["priceLowLimit"])+'\n'+'股票類別：'+data['typeZhTw'])
        else:
            text = ('交易幣別：'+data['currency']+'\n'+'股票中文簡稱：'+data['nameZhTw']+'\n'+'開盤參考價：'+ str(data['priceReference'])+'\n'+
                '漲停價：'+str(data[ 'priceHighLimit'])+'\n'+'跌停價：'+str(data["priceLowLimit"])+'\n'+'股票類別：'+data['typeZhTw'])
        
       
        update.callback_query.message.reply_text(text)
        

    if update.callback_query.data == 'trade':
        df2 = intraday.quote(apiToken=api_token,symbolId=num,output='raw')
        df3 = df2['trade']
        text = ('● '+data['nameZhTw']+'('+num+')'+'最新一筆交易：'+'\n'+'成交價：'+str(df3['price'])+'\n'+'成交張數：'+str(df3['unit'])+'\n'+'成交量：'+str(df3['volume'])+'\n'+
                                                                                                     '成交序號：'+str(df3['serial']))
        update.callback_query.message.reply_text(text)
        




dispatcher = Dispatcher(bot, None)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, info))
dispatcher.add_handler(CallbackQueryHandler(getClickButtonData))

if __name__ == '__main__':
    app.run()
