# Cheap-Gas-Notify
A python script which collects gas prices daily and notifies when its the cheapest.

You will need an API key/token to be able to use this script.
visit https://collectapi.com/api/gasPrice/gas-prices-api then click "Try Free" to subscribe. Its free with 100 free api calls per month.
then copy the API key/token from your profile at the top right.

then you can just run the script and it'll tell you what flags and arguments are required.<br>
currently it only works in USA

so the bare minimum flag/argument it needs are:<br>
`--state XX` (2 letter code)<br>
`--city yourCity`<br>
`--receiver emailTO@gmail.com` (a person/youself)<br>
`--sender emailFROM@gmail.com emailPASSWORD` (you'll need to edit the config file and paste your password, to prevent history of your pass)<br>
`--token TOKEN_HERE` (the one you got from collectapi.com)<br>

Optional:<br>
`--data /path/to/file` (by default it's be with your config file)

the config file will be store in your home directory<br>
`/home/user/Cheap-Gas-Notify/config.txt`

you can manually put all these information in the config file too instead of passing them as argument to python<br>
Example:<br>
```state NY
city new york
receiver emailTO@gmail.com
sender emailFROM@gmail.com PASSWORD
token TOKEN_HERE
data /home/USER/Cheap-Gas-Notify/gas_data_NY.pkl```
