```markdown
# Unit Test Cases

## 1. Passenger Validation

| ID | Scenario | Expected Result |
|---|---|---|
| P01 | One adult passenger | Valid |
| P02 | Six passengers | Valid |
| P03 | Seven passengers | Rejected |
| P04 | No adult passengers | Rejected |
| P05 | Negative age | Rejected |
| P06 | Age 0 | Valid child, free |
| P07 | Age 4 | Valid child, free |
| P08 | Age 5 | 50% adult fare |
| P09 | Age 11 | 50% adult fare |
| P10 | Age 12 | 75% adult fare |
| P11 | Age 17 | 75% adult fare |
| P12 | Age 18 | Adult fare |

## 2. Group Discount

| ID | Passengers | Expected Discount |
|---|---:|---:|
| G01 | 1 | 0% |
| G02 | 2 | 0% |
| G03 | 3 | 5% |
| G04 | 4 | 5% |
| G05 | 5 | 10% |
| G06 | 6 | 10% |

## 3. Optional Services

| ID | Scenario | Expected Result |
|---|---|---|
| S01 | Insurance for one passenger | $80 |
| S02 | Insurance for three passengers | $240 |
| S03 | Wi-Fi for two passengers for 7 nights | $210 |
| S04 | Shore excursion for two passengers | $240 |
| S05 | No optional services | $0 |

## 4. Promotional Codes

| ID | Scenario | Expected Result |
|---|---|---|
| PR01 | Valid SUMMER10 | Applied |
| PR02 | Valid FIRST150 | Applied |
| PR03 | Valid CREW25 | Applied |
| PR04 | Expired WINTER5 | Rejected |
| PR05 | Unknown code | Rejected |
| PR06 | Spend below minimum | Rejected |
| PR07 | Total usage limit reached | Rejected |
| PR08 | Customer usage limit reached | Rejected |
| PR09 | Exactly minimum spend | Accepted |
| PR10 | Just below minimum spend | Rejected |

## 5. Capacity

| ID | Scenario | Expected Result |
|---|---|---|
| C01 | Booking within available capacity | Accepted |
| C02 | Booking exactly remaining capacity | Accepted |
| C03 | Booking beyond remaining capacity | Rejected |
| C04 | Cruise capacity is zero | Rejected |

## 6. Pricing

| ID | Scenario | Expected Result |
|---|---|---|
| PRC01 | Adult-only booking | Correct adult fare |
| PRC02 | Adult + child age 4 | Child is free |
| PRC03 | Adult + child age 10 | Child pays 50% |
| PRC04 | Adult + child age 15 | Child pays 75% |
| PRC05 | Group discount applied | Correct cruise discount |
| PRC06 | Optional services included | Correct service total |
| PRC07 | Promotional discount applied | Correct discounted subtotal |
| PRC08 | Tax applied | Correct 12% tax |
| PRC09 | Combined pricing scenario | Correct final total |

## 7. Booking

| ID | Scenario | Expected Result |
|---|---|---|
| B01 | Valid booking confirmation | Booking created |
| B02 | Booking reference generated | Unique reference |
| B03 | Successful booking reduces capacity | Capacity updated |
| B04 | Failed booking does not reduce capacity | Capacity unchanged |
| B05 | Promotion redemption recorded | Redemption created |

## 8. Historical Pricing

| ID | Scenario | Expected Result |
|---|---|---|
| H01 | Create booking and retrieve it | Original amount returned |
| H02 | Change cruise fare after booking | Old booking amount unchanged |
| H03 | Change tax rule after booking | Old tax amount unchanged |
| H04 | Change promotional rule after booking | Old promotional discount unchanged |
| H05 | Retrieve passenger/service snapshot | Original booking details available |

## 9. Failure Scenarios

The system should fail safely without partially updating persistent state when:

- booking validation fails
- capacity is insufficient
- promotional validation fails
- database persistence fails during confirmation

## 10. Automated Integration Tests

The automated test suite covers:

- successful booking creation
- unique booking reference generation
- capacity reduction after successful booking
- rejection when capacity is insufficient
- retrieval of a booking by reference
- promotional redemption persistence
- historical pricing preservation after a cruise fare changes