# Installation instructions

1.  Start a new project or open an existing one on [Google Cloud Platform](https://console.cloud.google.com/).

1.  Make sure you have billing enabled in the [Billing dashboard](https://console.cloud.google.com/billing/00DA00-35C891-A50E02?project=test-coviduci).

1.  Create a new VM instance in the [Compute Engine dashboard](https://console.cloud.google.com/billing).

   1.  Choose machine type (the meatier, the more you'll get charged).

   1.  Change Boot disk to Ubuntu 18.04 LTS.

   1.  Select to allow both HTTP and HTTPS traffic.

   1.  Once created, take note of the External IP. We will refer to this as `${IP}` from now on.

1.  In [Firewall rules](https://console.cloud.google.com/networking/firewalls), make sure you have rules allowing connections on ports `tcp:80`, `tcp:8989` (HTTP) and `tcp:443` (HTTPS) (with `IP ranges: 0.0.0.0/0` in Filters).

1.  Connect to the device via `ssh` either by web ssh or using the `gcloud` command.

1.  Once connected to the machine, get the link from [Miniconda](https://docs.conda.io/en/latest/miniconda.html), download it, and run it . For example:

    ```
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    chmod +x Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh
    ```

1.  Close and re-open your shell to make sure path variables are updated.

1.  Create a new conda environment and activate it:

    ```
    conda create -n coviduci python=3.7
    conda activate coviduci
    ```

1.  Once connected to the machine, run:

    ```
    git clone git@github.com:psc-g/coviduci-ec.git
    ```

    (You may need to generate a new SSH key for this machine, see instructions [here](https://help.github.com/en/enterprise/2.17/user/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)).

1.  Run the following set of commands:

    ```
    cd coviduci-ec
    pip install -r requirements.txt
    pip install -e .
    ```

1.  Run `mkdir ~/resources` and copy the files `~/coviduci-ec/resources/coviduci.toml` and `~/coviduci-ec/resources/coviduci.env` to `~/resources`, and modify the values appropriately.

1.  Run the script to populate the database. In addition to creating the `hospitales`, `insumos`, and `medicaciones` tables, this script will also prompt you to create display names and passwords for the administrator account, as well as an account for viewing aggregated hospital data (for example, for the ministry of health):

    ```
    python scripts/initialize_db.py --config=/home/${USER}/resources/coviduci.toml --dotenv_path=/home/${USER}/resources/coviduci.env
    ```

1.  It's a good idea to create a test copy of the config file and database (you can keep them in the same directory):

    ```
    cp ~/resources/coviduci.toml ~/resources/test.toml
    cp ~/resources/coviduci.db ~/resources/test.db
    ```

    In `test.toml`, update the value of `sqlite_path` to point to `test.db`.

1.  Run the test server:

    ```
    cd /home/${USER}/coviduci-ec
    python /home/${USER}/coviduci-ec/scripts/run_server.py --port 8989 --dotenv_path=/home/${USER}/resources/coviduci.env --config=/home/${USER}/resources/test.toml
    ```

    In your browser, go to `http://${IP}:8989`.

1.  Log in as the administrator. If you go to "Lista de hospitales" you will see that the admin and ministry accounts are listed as hospitals. To exclude these, modify the `TEST_HOSPITALS` variable in `coviduci/www/handlers/admin.py`.

1.  When logged in as the admin, click on "Agregar hospital" and add a new hospital. It's a good idea to add some fake tests ones to try out the system (and update `TEST_HOSPITALS` accordingly, as indicated above). Log out (by clicking on "Salir") and try logging in with the new hospital. If all of this works, we're ready to try to deploy the real server!

1.  Install certbot, instructions [here](https://certbot.eff.org/), select `Nginx` for Software, and `Ubuntu 18.04 LTS` for System. Instructions will look something like:

    ```
    sudo apt-get update
    sudo apt-get install software-properties-common
    sudo add-apt-repository universe
    sudo add-apt-repository ppa:certbot/certbot
    sudo apt-get update
    sudo apt-get install certbot python-certbot-nginx
    ```

1.  Copy the `nginx` configuration files and modify them accordingly.

    ```
    sudo cp ~/coviduci-ec/resources/www.coviduci.com /etc/nginx/sites-available
    sudo ln -s /etc/nginx/sites-available/www.coviduci.com /etc/nginx/sites-enabled/www.coviduci.com
    ```

1.  Run `sudo certbot --nginx` and select `www.coviduci.com` (or whatever server name you chose). Once this is done, uncomment the `ssl_certificate` lines in `/etc/nginx/sites-available/www.coviduci.com`.

    * Note that for this to work, you need to have a registered domain name, and the IP mapping for this domain name needs to be the one for your virtual machine, otherwise `certbot` will fail.

1.  Copy the file `~/coviduci-ec/resources/coviduci.service` to `/lib/systemd/system/coviduci.service` (you will need to run this as `sudo`). Modify the paths appropriately, to match your username.

1.  Ensure `nginx` is running (you should see a green "active (running)" line in the output:

    ```
    sudo systemctl status nginx
    ```

1.  Start your server!

    ```
    sudo systemctl status coviduci
    ```

1.  Once your site is up, it's probably best to test your changes by running the test server (see instrucitons above), and then restarting the real server. A useful way of restarting your server and seeing the output logs:

    ```
    sudo systemctl restart coviduci &&  tail /var/log/syslog  -n 100 -f-f
    ```

1.  Good luck!
