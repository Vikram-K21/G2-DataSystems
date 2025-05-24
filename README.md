

## Get started by:

Firstly, run main.py
```bash
python main.py
```

Secondly, run the Flask Backend

```bash
cd backend
python app.py
```

Finally, running the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result. 

If you wish to see if the backend works, open http://localhost:5000

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

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