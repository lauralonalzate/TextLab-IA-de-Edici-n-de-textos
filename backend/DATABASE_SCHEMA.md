# Esquema de Base de Datos - TextLab

## Diagrama ER (Entidad-Relación)

```
┌─────────────────────────────────────────────────────────────────┐
│                           users                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK  id              UUID                                         │
│     email           VARCHAR(255) UNIQUE                         │
│     full_name       VARCHAR(255)                                │
│     password_hash   VARCHAR(255)                                │
│     role            ENUM(student, teacher, researcher, admin)   │
│     created_at      TIMESTAMP WITH TIME ZONE                     │
│     updated_at      TIMESTAMP WITH TIME ZONE                     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ 1
                            │
                            │ *
┌─────────────────────────────────────────────────────────────────┐
│                        documents                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK  id              UUID                                         │
│ FK  owner_id        UUID -> users.id (ON DELETE CASCADE)        │
│     title           VARCHAR(255)                                │
│     content         TEXT                                         │
│     metadata        JSONB                                        │
│     is_public       BOOLEAN                                      │
│     created_at      TIMESTAMP WITH TIME ZONE                     │
│     updated_at      TIMESTAMP WITH TIME ZONE                     │
│                                                                   │
│ INDEX: owner_id                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ 1
                            │
                            │ *
        ┌───────────────────┴───────────────────┐
        │                                       │
        │ *                                     │ *
┌───────────────────────────┐    ┌───────────────────────────┐
│       citations            │    │      references           │
├───────────────────────────┤    ├───────────────────────────┤
│ PK  id              UUID   │    │ PK  id              UUID   │
│ FK  document_id     UUID   │    │ FK  document_id     UUID   │
│     citation_text   TEXT   │    │     ref_text        TEXT   │
│     citation_key    VARCHAR│    │     ref_key         VARCHAR│
│     parsed          JSONB  │    │     parsed          JSONB  │
│     created_at      TIMESTAMP│  │     created_at      TIMESTAMP│
│     updated_at      TIMESTAMP│  │     updated_at      TIMESTAMP│
│                           │    │                           │
│ INDEX: document_id        │    │ INDEX: document_id        │
└───────────────────────────┘    └───────────────────────────┘
        │                                       │
        │                                       │
        │ citation_key ──────── ref_key ───────┘
        │   (referencia lógica)
        │
┌─────────────────────────────────────────────────────────────────┐
│                      export_jobs                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK  id              UUID                                         │
│ FK  document_id     UUID -> documents.id (ON DELETE CASCADE)    │
│ FK  user_id         UUID -> users.id (ON DELETE CASCADE)        │
│     status          ENUM(queued, running, done, failed)         │
│     result_path     VARCHAR(500)                                │
│     created_at      TIMESTAMP WITH TIME ZONE                     │
│     finished_at     TIMESTAMP WITH TIME ZONE (nullable)          │
│                                                                   │
│ INDEX: document_id, user_id                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      audit_logs                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK  id              UUID                                         │
│ FK  user_id         UUID -> users.id (ON DELETE SET NULL)       │
│     action          VARCHAR(100)                                 │
│     details         JSONB                                        │
│     timestamp       TIMESTAMP WITH TIME ZONE                     │
│                                                                   │
│ INDEX: user_id, timestamp                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Relaciones

1. **users → documents** (1:N)
   - Un usuario puede tener múltiples documentos
   - `ON DELETE CASCADE`: Si se elimina un usuario, se eliminan sus documentos

2. **documents → citations** (1:N)
   - Un documento puede tener múltiples citas
   - `ON DELETE CASCADE`: Si se elimina un documento, se eliminan sus citas

3. **documents → references** (1:N)
   - Un documento puede tener múltiples referencias
   - `ON DELETE CASCADE`: Si se elimina un documento, se eliminan sus referencias

4. **documents → export_jobs** (1:N)
   - Un documento puede tener múltiples trabajos de exportación
   - `ON DELETE CASCADE`: Si se elimina un documento, se eliminan sus trabajos de exportación

5. **users → export_jobs** (1:N)
   - Un usuario puede tener múltiples trabajos de exportación
   - `ON DELETE CASCADE`: Si se elimina un usuario, se eliminan sus trabajos de exportación

6. **users → audit_logs** (1:N)
   - Un usuario puede tener múltiples registros de auditoría
   - `ON DELETE SET NULL`: Si se elimina un usuario, los logs se mantienen pero user_id se pone NULL

## Índices

- `users.email` - UNIQUE INDEX (búsqueda por email)
- `documents.owner_id` - INDEX (búsqueda de documentos por usuario)
- `citations.document_id` - INDEX (búsqueda de citas por documento)
- `references.document_id` - INDEX (búsqueda de referencias por documento)
- `export_jobs.document_id` - INDEX (búsqueda de trabajos por documento)
- `export_jobs.user_id` - INDEX (búsqueda de trabajos por usuario)
- `audit_logs.user_id` - INDEX (búsqueda de logs por usuario)
- `audit_logs.timestamp` - INDEX (búsqueda de logs por fecha)

