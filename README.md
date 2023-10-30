# Himawari Download
## Assisting you in downloading Himawari satellite imagery data more reliably

### File Configuration:
```python
config = {
    "user": "*******",          # Username
    "passwd": "*******",        # Password
    "start_date": "2019-01-01",  # Start Date
    "end_date": "2019-01-02",    # End Date
    "hour_list": ['03', '04', '05'],  # Hours Selection
    "output_path": "",   # Output Path
} 
```

**Note:**
In this example, the data download is configured for the Japan region. You can download different datasets by modifying the `parent_path` file path and the `pattern` regular expression. if you have any questions, please feel free to contact me(zuochen1999@mail.bnu.edu.cn).

_Cheers!_

