#RSI and OBV Divergence Indicator Bot created by rpp

import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import numpy
import aiohttp

#Bot Command Prefix
bot = commands.Bot(command_prefix='$')
client = discord.Client()

#Launching Barry Statement
@bot.event
async def on_ready():
    print('Ready to analyze')
    client.loop.create_task(background_running_analysis())

#Result updater background task
async def background_running_analysis():
    #Run indefinitely
    results_dict = {}
    bot.results_dict = results_dict
    while True:
        coin_list1 = ['NAVBTC'] #pour testing
        coin_list = ['ADABTC','ADXBTC','AEBTC','AIONBTC','AMBBTC','APPCBTC','ARKBTC','ARNBTC','ASTBTC','BATBTC','BCCBTC','BCDBTC','BCPTBTC','BLZBTC','BNBBTC','BNTBTC','BQXBTC','BRDBTC','BTGBTC','BTSBTC','CDTBTC','CHATBTC','CMTBTC','CNDBTC','DASHBTC','DGDBTC','DLTBTC','DNTBTC','EDOBTC','ELFBTC','ENGBTC','ENJBTC','EOSBTC','ETCBTC','ETHBTC','EVXBTC','FUELBTC','FUNBTC','GASBTC','GTOBTC','GVTBTC','HSRBTC','ICNBTC','ICXBTC','INSBTC','IOSTBTC','IOTABTC','KMDBTC','KNCBTC','LENDBTC','LINKBTC','LRCBTC','LSKBTC','LTCBTC','LUNBTC','MANABTC','MCOBTC','MDABTC','MODBTC','MTHBTC','MTLBTC','NANOBTC','NAVBTC','NCASHBTC','NEBLBTC','NEOBTC','NULSBTC','OAXBTC','OMGBTC','ONTBTC','OSTBTC','PIVXBTC','POABTC','POEBTC','POWRBTC','PPTBTC','QTUMBTC','RCNBTC','RDNBTC','REQBTC','RLCBTC','RPXBTC','SALTBTC','SNMBTC','SNTBTC','SNGLSBTC','STEEMBTC','STORJBTC','STRATBTC','SUBBTC','TNBBTC','TNTBTC','TRIGBTC','TRXBTC','VENBTC','VIABTC','VIBBTC','VIBEBTC','WABIBTC','WAVESBTC','WINGSBTC','WTCBTC','XLMBTC','XMRBTC','XVGBTC','XRPBTC','XZCBTC','YOYOBTC','ZECBTC','ZRXBTC','BCCUSDT','BNBUSDT','BTCUSDT','ETHUSDT','LTCUSDT','NEOUSDT']
        #Calculate for all time periods 
        time_periods1 = ['2h']
        time_periods = ['1h','2h','4h','6h','8h','12h','1d']
        for period in time_periods:
            results_fr = []
            results_current_div = []
            for coin in coin_list:
                normal_results = []
                results_cd = []            
                coin_data = await get_candles(coin,60,period)
                normal_results, results_current_div = analysis_RSIOBV(coin,coin_data,normal_results,results_current_div)
                if len(normal_results) > 0:
                    for idx in range(len(normal_results)):
                        results_fr.append(normal_results[idx])
                if len(results_current_div) > 0:
                    for idx in range(len(results_current_div)):
                        results_cd.append(results_current_div[idx])
            results_dict[period] = (results_fr, results_cd)
            await asyncio.sleep(10)

#Bot command for analysis results
@bot.command(pass_context=True)
async def histdiv(ctx,time_frame:str):
    valid_time_frames = ['1hour','2hour','4hour','6hour','8hour','12hour','1day']
    if time_frame not in valid_time_frames:
        await bot.say('Not a valid timeframe to analyze for')
        await bot.say('Valid Time Frames are: {}'.format(valid_time_frames))
    else:
        #Retrieve results from background task
        tf_to_period = {'1hour':'1h','2hour':'2h','4hour':'4h','6hour':'6h','8hour':'8h','12hour':'12h','1day':'1d'}
        results_dict = bot.results_dict
        results_desired_fr,results_desired_cd = results_dict[tf_to_period[time_frame]]
        #Format results into lists of strings for embedding and avoiding max length for messages in discord and embeds and based on value of 'score'
        full_results_sorted = sort_based_on_score(results_desired_fr)
        full_results_str_list = full_results_to_str(full_results_sorted)
        tf_converter_print = {'1hour':'1 hour','2hour':'2 hour','4hour':'4 hour','6hour':'6 hour','8hour':'8 hour','12hour':'12 hour','1day':'1 day'}
        #Print embed statements to Discord
        for idx in range(len(full_results_str_list)):
            embed_title = 'Historical Divergences within 28 periods for {} Candles: Part {} of {}'.format(tf_converter_print[time_frame],idx + 1,len(full_results_str_list))
            message = full_results_str_list[idx][0]
            embed = discord.Embed(title=embed_title,description=message)
            await bot.say(embed=embed)

@bot.command(pass_context=True)
async def currentdiv(ctx,time_frame:str):
    valid_time_frames = ['1hour','2hour','4hour','6hour','8hour','12hour','1day']
    if time_frame not in valid_time_frames:
        await bot.say('Not a valid timeframe to analyze for')
        await bot.say('Valid Time Frames are: {}'.format(valid_time_frames))
    else:
        #Retrieve results from background task
        tf_to_period = {'1hour':'1h','2hour':'2h','4hour':'4h','6hour':'6h','8hour':'8h','12hour':'12h','1day':'1d'}
        results_dict = bot.results_dict
        results_desired_fr,results_desired_cd = results_dict[tf_to_period[time_frame]]
        #Format results into lists of strings for embedding and avoiding max length for messages in discord and embeds and based on value of 'score'
        cd_results_sorted = sort_based_on_score(results_desired_cd
        cdr_str_list = current_div_results_to_str(cd_results_sorted)
        #Reorganize results based on score value
       
        tf_converter_print = {'1hour':'1 hour','2hour':'2 hour','4hour':'4 hour','6hour':'6 hour','8hour':'8 hour','12hour':'12 hour','1day':'1 day'}
        #Print embed statements to Discord
        for idx in range(len(cdr_str_list)):
            embed_title = 'Current Possible RSI Divergences (Part {} of {})'.format(idx + 1,len(cdr_str_list))
            message = cdr_str_list[idx][0]
            embed = discord.Embed(title=embed_title,description=message)
            await bot.say(embed=embed)

@bot.command(pass_context=True)
async def helpme(ctx):
    embed = discord.Embed(title='Help Guide',description='A quick overview of the bot')
    embed.set_author(name='RSI and OBV Divergence Indicator')
    embed.add_field(name='Valid Time Frames (written how is):',value='1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day')
    embed.add_field(name='Commands:',value='$helpme,$histdiv (time frame),$currentdiv (time frame)')
    embed.add_field(name='Calculates/Finds?',value='RSI and OBV Divergences (within 28 periods) and possible forming RSI Divergences')
    await bot.say(embed=embed)

async def get_candles(coin,limitK,period):
    """Uses aiohttp to download data from Binance based on coin, period, and limit
    Parameters:
        coin;str
        limitK;number
        period;str
    Returns:
        coin_data;list of dictionaries
    """
    limitK = str(limitK)
    ENDPOINT = 'https://api.binance.com/api/v1/klines'
    url = ENDPOINT + '?symbol=' + coin + '&interval=' + period + '&limit=' + limitK
    async with aiohttp.ClientSession() as session
        async with session.get(url) as resp:
            if resp.status == 200:
                coin_data = await resp.json()
    return [{
        "open": d[1],
        "close": d[4],
        "volume": d[5],
    } for d in coin_data]

def calculateRSI(coin_data):
    """Calculates RSI for coin
    Parameters:
        coin_data; list of dictionaries
    Returns:
        list_RSI;list(list of RSIs(floats))
        last_avg_gain;float (to be used in void RSI calculations)
        last_avg_loss;float (to be used in void RSI calculations)
    """
    import numpy
    change_list = []
    #Download and organize Price data into list
    for idx in range(len(coin_data)):
        change = float(coin_data[idx]['close'])-float(coin_data[idx]['open'])        
        change_list.append(change)
    #creat total avg gain and loss lists with correct 0 values based on gains and losses
    list_gain = []
    list_loss = []
    for change in change_list:
        if change > 0:
            list_gain.append(abs(change))
            list_loss.append(0)
        elif change < 0:
            list_gain.append(0)
            list_loss.append(abs(change))
        elif change == 0:
            list_gain.append(0)
            list_loss.append(0)
    #calculate RS based off change and initialize last_avg_gain and last_avg_loss 
    list_rs = []
    last_avg_gain = 0
    last_avg_loss = 0
    for idx in range(13,60):
        if idx == 13:
            avg_gain = numpy.mean(list_gain[0:14])
            avg_loss = numpy.mean(list_loss[0:14])
            new_rs = avg_gain / avg_loss
            list_rs.append(new_rs)
            prev_avg_gain = avg_gain
            prev_avg_loss = avg_loss
        elif idx > 13:
            avg_gain = ((prev_avg_gain * 13) + list_gain[idx]) / 14
            avg_loss = ((prev_avg_loss * 13) + list_loss[idx]) / 14
            new_rs = avg_gain/avg_loss
            list_rs.append(new_rs)
            prev_avg_gain = avg_gain
            prev_avg_loss = avg_loss
        #for void price calculations
        if idx == 58:            
            last_avg_gain = prev_avg_gain
            last_avg_loss = prev_avg_loss
    #calculate RSI based off list_rs
    list_RSI=[]
    for rs in list_rs:
        rsi = (100 - (100 / (1 + rs)))
        rsi = round(rsi,2)
        list_RSI.append(rsi)
    #reduce list_RSI to last 28 rsi's for analysis
    list_RSI = list_RSI[-28:]
    return list_RSI,last_avg_gain,last_avg_loss

def calculate_obv(coin_data):
    """Calculate OBV for coin
    Parameters:
        coin;str
        coin_data; list of dictionaries
    Returns:
        list_OBV;list(list of floats)
    """
    #Initialize list_OBV with starting value at 0 and prev_OBV with an arbitrary value of 0
    list_OBV = [0]
    prev_OBV = 0
    #Calculate OBV
    for idx in range(1,len(coin_data)):
        change_day = float(coin_data[idx]['close']) - float(coin_data[idx-1]['close'])
        change_volume = float(coin_data[idx]['volume'])
        if idx == 1:
            if change_day > 0:
                new_OBV = change_volume
            elif change_day < 0:
                new_OBV = 0 - change_volume
            else:
                new_OBV = 0
        elif idx > 1: 
            if change_day > 0:
                new_OBV = prev_OBV + change_volume
            elif change_day < 0:
                new_OBV = prev_OBV - change_volume
            else:
                new_OBV = prev_OBV
        new_OBV = round(new_OBV,2)
        list_OBV.append(new_OBV)
        prev_OBV = new_OBV
    #Remove the 0 from the beginning of the list
    zero_check = True
    while zero_check == True:
        if list_OBV[0] == 0:
            del list_OBV[0]
        if list_OBV[0] != 0:
            zero_check = False
    #Reduce list_OBV to last 28 OBVs for later analysis
    list_OBV = list_OBV[-28:]
    return list_OBV

def price_per_period(coin_data):
    """Extracts the closing prices for each period for a coin from coin_data
    Parameters:
        coin_data;list of floats
    Returns:
        list_price;list of floats
    """
    #print(type(coin_data)
    #Initialize list_price
    list_price = []
    #Extract closing price for each period and add to list_price
    for idx in range(len(coin_data)):
        price = float(coin_data[idx]['close'])
        list_price.append(price)
    #Reduce list_price to the last 28 closing prices for later analysis
    list_price = list_price[-28:]
    return list_price

def comparator(list_price,list_RSI,list_OBV,last_avg_gain,last_avg_loss):
    """Determines trend of Price, RSI, and OBV
        Determines if RSI bullish divergence or OBV bullish divergence occurs
    Parameters:
        list_price;list of floats
        list_RSI;list of floats
        list_OBV;list of floats
        last_avg_gain;float
        last_avg_loss;float
    Returns:
        trend_price;bool
        trend_RSI;bool
        trend_OBV;bool
        score_RSI;float
        score_OBV;float
        current_div_RSI;tuple (bool,float)
        void_price;float 
        rsi_div_idx;list
        obv_div_idx;list
    """
    #Intitialize lists 
    ll_price_broad = []
    ll_idx = []
    ll_idx_broad = []
    ll_price = []
    #Initialize idx_counter to determine index of local lows (ll = local lows)
    idx_counter = 1
    #Find local lows of Price (ll_price_broad)
    for idx in range(1,len(list_price) - 1):
        if list_price[idx] < list_price[idx-1] and list_price[idx] < list_price[idx+1]:
            ll_price_broad.append(list_price[idx])
            ll_idx_broad.append(idx_counter)
        idx_counter += 1
    #reset idx_counter
    idx_counter = 1
    #Find local lows of the local lows for Price (ll_price)
    for idx in range(1,len(ll_price_broad) - 1):
        if ll_price_broad[idx] < ll_price_broad[idx-1] and ll_price_broad[idx] < ll_price_broad[idx+1]:
            ll_price.append(ll_price_broad[idx])
            ll_idx.append(ll_idx_broad[idx_counter])
        idx_counter += 1
    #Determine if endpoints could be considered lows (despite not having a high on one side) and add their indices accordingly
    #Find if first price is considered to be a low
    if ll_price_broad[0] < ll_price_broad[1]:
        ll_price.insert(0,ll_price_broad[0])
        ll_idx.insert(0,ll_idx_broad[0])
    #Find if last price is considered to be a low
    if ll_price_broad[-1] < ll_price_broad[-2]:
        ll_price.append(ll_price_broad[-1])
        ll_idx.append(ll_idx_broad[-1])
    #Find local lows for RSI and OBV according to the local low indices (ll_idx) for comparison against Price
    #Initialize ll_RSI and ll_OBV
    ll_RSI = []
    ll_OBV = []
    #Add correct RSIs and OBVs according to ll_idx
    for idx in ll_idx:
        ll_RSI.append(list_RSI[idx])
        ll_OBV.append(list_OBV[idx])
    """
    #Testing statements for bug fixing (unnecessary for normal use)
    print(ll_idx_broad)
    print(ll_idx)
    print('Prices',list_price)
    print('Low Prices:',ll_price)
    print('RSIs:',list_RSI)
    print('Low RSIs:',ll_RSI)
    print('OBVs:',list_OBV)
    print('Low OBVs:',ll_OBV)
    plot(list_price,'price total')
    plot(ll_price,'price lows')
    plot(list_RSI,'rsi total')
    plot(ll_RSI,'rsi lows')
    plot(list_OBV,'obv total')
    plot(ll_OBV,'obv lows')
    """
    #Determine the trend of Price, RSI, and OBV (True = Up; False = Down)
    #Initialize trends for Price, RSI, and OBV; Desired Trends: Price --> False; RSI --> True; OBV --> True)
    trend_price = True 
    trend_RSI = False
    trend_OBV = False
    
    #Determine trend_price
    threshold = 1
    counter_trend_price = 0
    #Adds 1 to counter_trend_price everytime price decreases between local lows in ll_price
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0:
            counter_trend_price += 1
    #Switches trend_price to False if there is 
    if counter_trend_price >= threshold:
        trend_price = False
        
    #Determine if RSI is currently diverging (current period)
    #Initialize current_div_RSI = (bool (True if diverging),score (how much the divergence is))
    current_div_RSI = (False,0)
    #Determine if RSi is currently diverging and calculate score (% change in price * RSI change)
    if list_price[-1] < ll_price[-1] and list_RSI[-1] > ll_RSI[-1]:
        (bool,score) = current_div_RSI
        score_div_RSI = abs(ll_RSI[-1] - list_RSI[-1])
        score_div_price = ((abs(ll_price[-1] - list_price[-1]) / (ll_price[-1])) * 100) + 1
        current_div_RSI = (True,round(score_div_RSI*score_div_price,2))
    #Calcualte void_price for RSI (the price at which the RSI will no longer be higher than the previous local low)
    void_price = 0
    #Calculate by continually decreasing price until RSI is below last local low RSI
    if current_div_RSI[0] == True:
        last_ll_rsi = ll_RSI[-1]
        void = False
        fake_price = list_price[-1]
        while void == False:
            fake_change = list_price[-2] - fake_price
            void_avg_gain = (last_avg_gain*13) / 14
            void_avg_loss = ((last_avg_loss*13) + fake_change) / 14
            void_RS = void_avg_gain / void_avg_loss
            void_rsi = 100 - (100 / (1 + void_RS))
            if void_rsi < last_ll_rsi:
                void_price = fake_price
                void = True
            fake_price -= (0.001 * fake_price)
            
    #Determine trend_RSI
    #Initialize score_RSI and counter_trend_RSI and rsi_div_idx
    score_RSI = []
    counter_trend_RSI = 0
    rsi_div_idx = []
    #Calculate score for any divergences and increase RSI divergence counter
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0 and (ll_RSI[idx] - ll_RSI[idx - 1]) > 0:
            counter_trend_RSI += 1
            score_RSI_RSI = abs(ll_RSI[idx - 1] - ll_RSI[idx])
            score_RSI_price = ((abs(ll_price[idx - 1] - ll_price[idx]) / (ll_price[idx - 1])) * 100) + 1
            score_RSI.append(round(score_RSI_RSI * score_RSI_price,2))
            #Record position of divergence 
            rsi_div_idx.append(28 - ll_idx[idx - 1])
            rsi_div_idx.append(28 - ll_idx[idx])
    
    #Determine trend_RSI based on number of divergences (at least 1)
    if counter_trend_RSI >= threshold:
        trend_RSI = True
        
    #determine trend_OBV
    #Initialize score_OBV and counter_trend_OBV
    score_OBV = []
    counter_trend_OBV = 0
    obv_div_idx = []
    #Calculate score for any divergences and increase OBV divergence counter
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0 and (ll_OBV[idx] - ll_OBV[idx - 1]) > 0:
            counter_trend_OBV += 1
            score_OBV_OBV = (abs(ll_OBV[idx - 1] - ll_OBV[idx]) / (ll_OBV[idx - 1])) * 100
            score_OBV_price = ((abs(ll_price[idx - 1] - ll_price[idx]) / (ll_price[idx - 1])) * 100) + 1
            score_OBV.append(abs(round(score_OBV_OBV *score_OBV_price,2)))
            #Record position of divergence
            obv_div_idx.append(28 - ll_idx[idx - 1])
            obv_div_idx.append(28 - ll_idx[idx])
    #Determine trend_OBV based on number of divergences (at least 1)
    if counter_trend_OBV >= threshold:
        trend_OBV = True
    return trend_price,trend_RSI,trend_OBV,score_RSI,score_OBV,current_div_RSI,void_price,rsi_div_idx,obv_div_idx

def comparator_results_compiler(coin,trend_RSI,trend_OBV,score_RSI,score_OBV,rsi_div_idx,obv_div_idx,full_results):
    """Prints results from comparator (divergence and score if applicable) and returns a tuple with (coin,divergences)
    Parameters:
        trend_price;bool
        trend_RSI;bool
        trend_OBV;bool
        coin;str
        score_RSI;float
        score_OBV;float
    Returns:
        full_results;list of dictionaries(dictionaries contain information on divergences)
    """
    #Add correct results and labels to full_results
    if trend_RSI == True and trend_OBV == True:
        for idx in range(len(score_RSI)):
            full_results.append({'coin':coin,'type div':'RSI Divergence','score':score_RSI[idx],'position':[rsi_div_idx[idx * 2],rsi_div_idx[(idx * 2) + 1]]})
        for idx in range(len(score_OBV)):
            full_results.append({'coin':coin,'type div':'OBV Divergence','score':score_OBV[idx],'position':[obv_div_idx[idx * 2],obv_div_idx[(idx * 2) + 1]]})
    elif trend_RSI == True and trend_OBV == False:
        for idx in range(len(score_RSI)):
            full_results.append({'coin':coin,'type div':'RSI Divergence','score':score_RSI[idx],'position':[rsi_div_idx[idx * 2],rsi_div_idx[(idx * 2) + 1]]})
    elif trend_RSI == False and trend_OBV == True:
        for idx in range(len(score_OBV)):
            full_results.append({'coin':coin,'type div':'OBV Divergence','score':score_OBV[idx],'position':[obv_div_idx[idx * 2],obv_div_idx[(idx * 2) + 1]]})
    return full_results

def current_div_results_compiler(coin,current_div_RSI,void_price,list_price,current_div_results):
    """Compiles information into current_div_results if there is a current RSI divergence forming
        Compiles coin,score,void price,current price into a dictionary and then adds the dictionary to the list current_div_results
    Parameters:
        coin;str
        current_div_RSI;tuple(bool,float)
        void_price;float
        list_price;list
        current_div_results;list of dictionaries (for storage of current divergence RSI data)
    Returns:
        current_div_results;list of dictionaries
    """
    if current_div_RSI[0] == True:
        void_price = '{:.8f}'.format(void_price)
        current_price = '{:.8f}'.format(list_price[-1])
        current_div_results.append({'coin':coin,'score':current_div_RSI[1],'void price':void_price,'current price':current_price})
    return current_div_results

def pre_comparator(list_price):
    """Smaller comparator to run before main comparator to prevent unnecessary calculations being performed 
        Determines trend of price
    Parameters:
        list_price;list
    Returns:
        trend_price;bool (True if downtrending)
    """
    #Initialize ll_price_broad and ll_price
    ll_price_broad = []
    ll_price = []
    #Find local lows of price
    for idx in range(1,len(list_price) - 1):
        if list_price[idx] < list_price[idx - 1] and list_price[idx] < list_price[idx + 1]:
            ll_price_broad.append(list_price[idx])
    #Find the local lows of the local lows for price
    idx_counter = 1
    for idx in range(1,len(ll_price_broad) - 1):
        if ll_price_broad[idx] < ll_price_broad[idx - 1] and ll_price_broad[idx] < ll_price_broad[idx + 1]:
            ll_price.append(ll_price_broad[idx])
    #Determine if endpoints of the list are lows (despite missing one point for comparison) and add if applicable
    if len(ll_price_broad) > 1: #Prevents error with list of len == 1
        if ll_price_broad[0] < ll_price_broad[1]:
            ll_price.insert(0,ll_price_broad[0])
        if ll_price_broad[-1] < ll_price_broad[-2]:
            ll_price.append(ll_price_broad[-1])
    #Determine trend_price
    trend_price = True
    threshold = 1
    counter_trend_price = 0
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0:
            counter_trend_price += 1
    if counter_trend_price >= threshold:
        trend_price = False
    return trend_price
        
coins_failure = ['CLOAKBTC','GRSBTC','QLCBTC','ONTBTC','POABTC','STORMBTC','SYSBTC','WPRBTC','XEMBTC','ZILBTC']

def analysis_RSIOBV(coin,coin_data,full_results,current_div_results):
    list_price = price_per_period(coin_data)
        #Runs full analysis if downtrend in price is detected
    if False == pre_comparator(list_price):
        #Calculates RSI and OBV 
        list_RSI,last_avg_gain,last_avg_loss = calculateRSI(coin_data)
        list_OBV = calculate_obv(coin_data)
         #Determines trend of Price, RSI, and OBV
        trend_price,trend_RSI,trend_OBV,score_RSI,score_OBV,current_div_RSI,void_price,rsi_div_idx,obv_div_idx = comparator(list_price,list_RSI,list_OBV,last_avg_gain,last_avg_loss)
        #test_plot(list_price,list_RSI,list_OBV) #This line is meant to be used for testing in coordination with coin_list1
        #Compile into dictionaries for mapping and results during printing
        full_results = comparator_results_compiler(coin,trend_RSI,trend_OBV,score_RSI,score_OBV,rsi_div_idx,obv_div_idx,full_results)
        current_div_results = current_div_results_compiler(coin,current_div_RSI,void_price,list_price,current_div_results)
    return full_results,current_div_results
        
def full_results_to_str(full_results):
    """Changes full_results (a list of dictionaries) into a multi-line str to be used in embed statements in Discord
    Parameters:
        full_results;list of dictionaries
    Returns:
        full_results_str;multi-line str formatted to fit embed statements
    """
    full_results_str_list = []
    temp_list = []
    result_message = ''
    for idx in range(len(full_results)):
        dct = full_results[idx]
        result = '**{}** | {} | Score: {} | Divergence from {} to {} periods ago'.format(dct['coin'],dct['type div'],dct['score'],dct['position'][1],dct['position'][0])
        result_message = result_message + result
        #organizes into groups of 13
        if (idx + 1) % 20 == 0 or idx == (len(full_results) - 1):
            temp_list.append(result_message)
            full_results_str_list.append(temp_list)
            temp_list = []
            result_message = ''
    return full_results_str_list

def current_div_results_to_str(current_div_results):
    """Changes current_div_results (a list of dictionaries) into a multi-line str to be used in embed statements in Discord
    Parameters:
        current_div_results;list of dictionaries
    Returns:
        cdr_str_list;list of strings with length under 1024 for embed fields to not give error
    """
    cdr_str_list = []
    temp_list = []
    result_message = ''
    #Formats result and adds to a temp_list which is used to not exceed char limit
    for idx in range(len(current_div_results)):
        dct = current_div_results[idx]
        result = '**{}** | Score: {} | Void Price: {} | Current Price: {}'.format(dct['coin'],dct['score'],dct['void price'],dct['current price'])
        result_message = result_message + result
        #organizes into groups of 7 to not exceed Character Limit 1024
        if (idx + 1) % 15 == 0 or idx == (len(current_div_results) - 1):
            temp_list.append(result_message)
            cdr_str_list.append(temp_list)
            temp_list = []
            result_message = ''
    return cdr_str_list

def sort_based_on_score(results):
    '''Sorts results based on their score back into a list
    Parameters:
        results;list of dictionaries
    Returns:
        sorted_results;list of dictionaries
    '''
    slist_score = [x['score'] for x in results]  
    slist_tuple = [(x,results[x]['score']) for x in range(len(results))]
    slist_score.sort()
    sorted_results = []
    for ascore in slist_score:
        for idx in range(len(slist_score)):
            if ascore == results[idx]['score']:
                sorted_results.append(results[idx])
    return sorted_results
    
bot.run('NDU3Nzc0NTU4MTcxMjM0MzA0.DgeAkw.tzs04tsHyxL1OI1GhVi6vVZhRkk')
