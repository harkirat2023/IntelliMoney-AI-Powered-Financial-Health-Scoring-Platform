# Receipt OCR & Manual Expense Import

**Phase:** 13 | **Version:** 1.13

## Overview

The Receipt OCR module provides end-to-end receipt scanning and automated expense creation. Images are uploaded, preprocessed with OpenCV (deskew, denoise, adaptive threshold, contrast enhancement), and passed to Tesseract via pytesseract for optical character recognition. Structured data (merchant, amount, date, time, currency) is extracted via regex, validated, and used to auto-create expense entries. The module supports 6 receipt statuses, maintains processing logs, and publishes lifecycle events. It comprises 2 models, 2 repositories, 4 services, and 8 REST endpoints consumed by 4 frontend pages.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          FRONTEND                                    │
│                                                                      │
│  ┌────────────────┐ ┌────────────────┐ ┌──────────────────┐         │
│  │ReceiptsOverview│ │ReceiptUpload   │ │ReceiptReview     │         │
│  │Page (grid +    │ │Page (drag-drop │ │Page (editable    │         │
│  │ status badges)  │ │  + camera)    │ │ fields + confirm)│         │
│  └───────┬────────┘ └───────┬────────┘ └────────┬─────────┘         │
│          │                  │                    │                   │
│  ┌───────┴──────────────────┴────────────────────┴──────────────┐   │
│  │                ReceiptsLayout (4-item nav)                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    ReceiptHistoryPage                        │   │
│  │                    (table with delete)                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
├─────────────────────┼───────────────────────────────────────────────┤
│                 API │ 8 routes                                      │
├─────────────────────┼───────────────────────────────────────────────┤
│                     BACKEND                                         │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    ReceiptService (orchestrator)              │   │
│  │  upload → validate → OCR → categorize → createExpense →     │   │
│  │  publishEvent                                                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────┐ ┌──────────────┐ ┌─────────────────────┐     │
│  │ImageProcessing   │ │OCRService    │ │ReceiptValidation    │     │
│  │Service           │ │(Tesseract    │ │Service              │     │
│  │(OpenCV: deskew,  │ │pytesseract   │ │(image size/format,  │     │
│  │ denoise, adaptive │ │ regex        │ │ field validation,   │     │
│  │ threshold,        │ │ extraction)  │ │ update validation)  │     │
│  │ contrast enhance) │ │              │ │                     │     │
│  └──────────────────┘ └──────────────┘ └─────────────────────┘     │
│                                                                      │
│  ┌────────────────────┐ ┌─────────────────────────┐                 │
│  │ Receipt Repo       │ │ ReceiptProcessingLog    │                 │
│  │                    │ │ Repo                    │                 │
│  └────────────────────┘ └─────────────────────────┘                 │
└──────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Models (2)

| Model | Fields / Description |
|---|---|
| **Receipt** | 16 fields including merchant, amount, date, time, currency, category, image path; status lifecycle: `uploaded` → `processing` → `processed` → `confirmed` → (or `failed` / `expired`) |
| **ReceiptProcessingLog** | Processing audit trail — timestamps, OCR output, confidence scores, errors |

### Repositories (2)

| Repository | Model |
|---|---|
| **ReceiptRepository** | `Receipt` |
| **ReceiptProcessingLogRepository** | `ReceiptProcessingLog` |

### Services (4)

| Service | Responsibility |
|---|---|
| **ImageProcessingService** | OpenCV pipeline: deskew, denoise (fastNlMeansDenoising), adaptive threshold, contrast enhancement (CLAHE) |
| **OCRService** | Tesseract via pytesseract; regex extraction for merchant name, amount, date, time, currency |
| **ReceiptValidationService** | Validates image size and MIME type on upload; validates extracted fields; enforces update constraints |
| **ReceiptService** | Orchestrator: upload (validate) → process (OCR) → categorize → createExpense → publishEvent |

### Receipt Statuses

```
uploaded → processing → processed → confirmed
                           ↓
                        failed
                        
uploaded → expired (after TTL)
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/receipts/upload` | Upload receipt image |
| POST | `/receipts/{id}/process` | Trigger OCR processing |
| POST | `/receipts/{id}/confirm` | Confirm processed receipt |
| GET | `/receipts` | List all receipts |
| GET | `/receipts/{id}` | Get receipt details |
| PATCH | `/receipts/{id}` | Update receipt fields |
| DELETE | `/receipts/{id}` | Delete receipt |
| GET | `/receipts/{id}/image` | Retrieve receipt image |

## Frontend Pages & Layout

### Pages (4)

| Page | Description |
|---|---|
| **ReceiptsOverviewPage** | Grid layout with status badges |
| **ReceiptUploadPage** | Drag-drop zone + camera capture |
| **ReceiptReviewPage** | Editable extracted fields with confirm action |
| **ReceiptHistoryPage** | Table view with delete capability |

### Layout

**ReceiptsLayout** provides a 4-item navigation header.

## Event Types (3)

| Event | Trigger |
|---|---|
| `receipt.uploaded` | Image uploaded and validated |
| `receipt.processed` | OCR completed (success or failure) |
| `receipt.confirmed` | User confirmed extracted data |

## Configuration

| Variable | Description | Default |
|---|---|---|
| `UPLOAD_DIR` | Directory for receipt image storage | `uploads/receipts/` |
| `MAX_UPLOAD_SIZE` | Maximum upload file size | 10 MB |
| `ALLOWED_MIME_TYPES` | Accepted image MIME types | `image/jpeg`, `image/png`, `image/tiff` |

## Status & Version

| Property | Value |
|---|---|
| Phase | 13 |
| Version | 1.13 |
| Backend directory | `backend/app/receipt_ocr/` |
| Models | 2 |
| Repositories | 2 |
| Services | 4 |
| Endpoints | 8 |
| Receipt fields | 16 |
| Receipt statuses | 6 |
| Image processing steps | 4 (deskew, denoise, threshold, contrast) |
| OCR engine | Tesseract (pytesseract) |
| Frontend pages | 4 |
