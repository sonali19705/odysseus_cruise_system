# Business Requirements

## 1. Objective

The Cruise Booking System allows customers to search available cruises, select passengers and optional services, calculate the total booking price, apply eligible promotional codes, and confirm bookings.

The system must preserve the exact pricing information used at the time of booking so that historical bookings remain reconstructable even if cruise fares, promotions, discounts, or tax rules change later.

## 2. Core Functional Requirements

### 2.1 Cruise Availability

The system should allow customers to view available cruises.

A cruise is bookable only when sufficient capacity exists for the requested number of passengers.

A cruise with zero remaining capacity is unavailable.

### 2.2 Passenger Rules

- Every booking must contain at least one adult.
- A maximum of 6 passengers is allowed per booking.
- Age 18 and above is considered an adult.
- Age 0–17 is considered a child.
- Ages 0–4 travel free.
- Ages 5–11 pay 50% of the adult fare.
- Ages 12–17 pay 75% of the adult fare.

### 2.3 Group Discounts

Group discount is based on the number of passengers:

| Passengers | Discount |
|---|---:|
| 1–2 | 0% |
| 3–4 | 5% |
| 5–6 | 10% |

The group discount applies only to the cruise fare and not to optional services.

### 2.4 Optional Services

The supported services are:

| Service | Price | Charging Rule |
|---|---:|---|
| Insurance | $80 | Per passenger |
| Wi-Fi | $15 | Per passenger per night |
| Shore Excursion | $120 | Per passenger |

### 2.5 Promotional Codes

The system supports the following seeded promotional codes:

- SUMMER10
- FIRST150
- CREW25
- WINTER5

Promotional codes must be validated for:

- existence
- validity dates
- total usage limit
- per-customer usage limit
- minimum spend

Expired or otherwise invalid promotional codes must not be applied.

### 2.6 Tax

A tax rate of 12% is applied.

The chosen calculation rule is:

1. Calculate cruise fare including child pricing.
2. Apply group discount to cruise fare.
3. Add optional services.
4. Apply a valid promotional discount.
5. Apply 12% tax to the resulting taxable amount.

The decision is documented explicitly because the specification leaves the tax point as a design exercise.

### 2.7 Booking Confirmation

A booking can be confirmed only after:

- passenger validation
- cruise capacity validation
- pricing calculation
- promotional code validation

A successful booking receives a unique booking reference.

### 2.8 Historical Pricing

A confirmed booking stores a pricing snapshot containing:

- cruise fare charged
- group discount
- optional services total
- promotional discount
- tax rate
- tax amount
- final amount
- passenger information
- service information

Historical bookings must not be recalculated using current cruise prices or current promotion rules.

## 3. Seed Data

The system is initialized with the cruises and promotional codes supplied in the assessment.

## 4. Assumptions and Design Decisions

### Tax Calculation

Tax is calculated after applying the promotional discount because the promotional discount reduces the amount charged to the customer.

### Group Discount

Group discount applies only to the cruise fare and does not reduce optional service prices.

### Minimum Promotional Spend

Minimum spend is checked against the subtotal before the promotional discount is applied.

### Historical Bookings

The final charged amounts and applicable pricing inputs are stored with the booking to ensure historical reproducibility.

### Currency

All prices are represented as monetary values in USD.

### Capacity

Capacity is reduced only after a booking is successfully confirmed.