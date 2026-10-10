# Frontend — Riesgo de deserción escolar

Next.js 16 (App Router) + TypeScript + Tailwind 4. Ver `docs/ARQUITECTURA.md` (sección Frontend) y el README de la raíz.

```bash
cp .env.example .env.local   # API_URL del backend
npm install
npm run dev                  # http://localhost:3000
```

Todas las llamadas a la API salen del servidor de Next.js (`lib/api.ts`); el token vive en una cookie `httpOnly`.
