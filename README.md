
# Cheap-Gas-Notify
A python script which collects gas prices daily and notifies when its the cheapest.

Currently it only works in USA

### Flags:
`--zip zipcode` (5 digit US zipcode)<br>
`--receiver emailTO@gmail.com` (a person/youself)<br>
`--sender emailFROM@gmail.com` (Gmail only. You'll need to edit the config file and paste your password next to this, to prevent storing your password in command history)<br>

Optional:<br>
`--data /path/to/file` (by default it'll be with your config file)


### Config file:
the config file will be store in your home directory<br>
`/home/user/Cheap-Gas-Notify/config.txt`

you can also manually put all these information in the config file too instead of passing them as arguments<br>
Example of config file (in any order):<br>
```
zip 12345
receiver emailTO@gmail.com
sender emailFROM@gmail.com PASSWORD
data /home/USER/Cheap-Gas-Notify/gas_data_NY.pkl
```
