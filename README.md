

## Get started by:

Firstly, create a .env file of your own in the root directory - for format, refer below to 'About .env'.

Secondly, run main.py to load your data into your Azure SQL Database
```bash
python main.py
```

Afterwards, run the Flask Backend

```bash
cd backend
python app.py
```

OR

```bash
python backend/app.py
```

Finally, running the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result. 

If you wish to see how the backend works, open http://localhost:5000/api, and use one of the following debug endpoints:
There is only 5 table names;
```bash
dbo.energy_fact
dbo.ev_fact
dbo.fuel_dim
dbo.suburb_dim
dbo.time_dim
dbo.vehicle_dim
```

```bash
http://localhost:5000/api/tables/<table_name>
http://localhost:5000/api/list-tables
http://localhost:5000/api/check-table/<table_name>
http://localhost:5000/api/table-info/<table_name>
http://localhost:5000/api/explore/<table_name>
http://localhost:5000/api/schemas
```

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## About .env

You will need to create a .env file of your own in the root directory - and it should be five lines:

```bash
DB_SERVER=
DB_NAME=
DB_USER=
DB_PASSWORD=
AZURE_SQL_CONNECTIONSTRING=;
```

Please contact any member of the group for the details of the .env if needed.