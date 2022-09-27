# Get Epg with issue

## Getting Started

### Prerequisites

* Python 3 (create your venv)

```
 python3 -m venv venv
```
* Activate your venv

```
 source venv/bin/activate
```

### Installing
1. Run pip command to install required libraries.

```
> pip install -r requirements.txt
```

## Usage
Insert the login data in the file `Utils/credentials.json`:

Example:
```
{
"apic_ip_address": "10.10.10.10",
"apic_port": "443",
"apic_admin_user": "admin",
"apic_admin_password": "XXXXXXX",
}
```

then run the script:

```
$python3 get_epg_with_issue.py
```

it will provide potential impacted EPG.
