"use client"

import { useState } from "react"
import Link from "next/link"
import { Plus, Search, Download, Eye, MoreHorizontal, CheckCircle, Clock, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const invoices = [
  {
    id: "INV-001",
    customer: "Acme Corporation",
    amount: "€1,250.00",
    status: "completed",
    date: "2024-01-15",
    type: "Factur-X",
    dueDate: "2024-02-15"
  },
  {
    id: "INV-002",
    customer: "Tech Solutions Ltd",
    amount: "€850.00",
    status: "processing",
    date: "2024-01-15",
    type: "Standard PDF",
    dueDate: "2024-02-15"
  },
  {
    id: "INV-003",
    customer: "Global Industries",
    amount: "€2,100.00",
    status: "completed",
    date: "2024-01-14",
    type: "Factur-X",
    dueDate: "2024-02-14"
  },
  {
    id: "INV-004",
    customer: "StartUp Inc",
    amount: "€450.00",
    status: "failed",
    date: "2024-01-14",
    type: "Factur-X",
    dueDate: "2024-02-14"
  },
  {
    id: "INV-005",
    customer: "Enterprise Corp",
    amount: "€3,200.00",
    status: "completed",
    date: "2024-01-13",
    type: "Factur-X",
    dueDate: "2024-02-13"
  },
  {
    id: "INV-006",
    customer: "Digital Agency",
    amount: "€750.00",
    status: "processing",
    date: "2024-01-12",
    type: "Standard PDF",
    dueDate: "2024-02-12"
  },
  {
    id: "INV-007",
    customer: "Consulting Group",
    amount: "€1,800.00",
    status: "completed",
    date: "2024-01-11",
    type: "Factur-X",
    dueDate: "2024-02-11"
  },
  {
    id: "INV-008",
    customer: "Manufacturing Co",
    amount: "€5,500.00",
    status: "completed",
    date: "2024-01-10",
    type: "Factur-X",
    dueDate: "2024-02-10"
  }
]

const getStatusColor = (status: string) => {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
    case "processing":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
    case "failed":
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="h-4 w-4" />
    case "processing":
      return <Clock className="h-4 w-4" />
    case "failed":
      return <AlertCircle className="h-4 w-4" />
    default:
      return <Clock className="h-4 w-4" />
  }
}

export default function InvoicesPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [typeFilter, setTypeFilter] = useState("all")

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = invoice.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         invoice.id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || invoice.status === statusFilter
    const matchesType = typeFilter === "all" || invoice.type === typeFilter
    
    return matchesSearch && matchesStatus && matchesType
  })

  return (
    <div className="container px-4 py-8 mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Invoices</h1>
          <p className="text-muted-foreground">
            Manage and track all your Factur-X invoices
          </p>
        </div>
        <Button asChild>
          <Link href="/invoices/new">
            <Plus className="mr-2 h-4 w-4" />
            Create Invoice
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Search and filter your invoices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search invoices..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="Factur-X">Factur-X</SelectItem>
                <SelectItem value="Standard PDF">Standard PDF</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Invoices Table */}
      <Card>
        <CardHeader>
          <CardTitle>Invoice List</CardTitle>
          <CardDescription>
            {filteredInvoices.length} of {invoices.length} invoices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredInvoices.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell className="font-medium">{invoice.id}</TableCell>
                    <TableCell>{invoice.customer}</TableCell>
                    <TableCell className="font-medium">{invoice.amount}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{invoice.type}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(invoice.status)}
                        <Badge className={getStatusColor(invoice.status)}>
                          {invoice.status}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>{invoice.date}</TableCell>
                    <TableCell>{invoice.dueDate}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Open menu</span>
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Download className="mr-2 h-4 w-4" />
                            Download PDF
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Download className="mr-2 h-4 w-4" />
                            Download XML
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>
                            Resend Invoice
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">
                            Delete Invoice
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          {filteredInvoices.length === 0 && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No invoices found matching your criteria.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}