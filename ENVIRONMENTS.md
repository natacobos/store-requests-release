# Values per environment

The solution has one environment variable and one connection reference.

- Environment variable `sr_ServiceDeskUrl`: the address of the IT service desk API.
- Connection reference `sr_ServiceDeskConnection`: the connection the flows use to call that API.

## DEV
- `sr_ServiceDeskUrl`: https://servicedesk-test.example.com/api
- `sr_ServiceDeskConnection`: connection id `c0nn-dev-4711`

## TST
- `sr_ServiceDeskUrl`: https://servicedesk-test.example.com/api
- `sr_ServiceDeskConnection`: connection id `c0nn-tst-5822`

## PRD
- `sr_ServiceDeskUrl`: https://servicedesk.example.com/api
- `sr_ServiceDeskConnection`: connection id `c0nn-prd-6933`
