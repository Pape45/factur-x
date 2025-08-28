"use client"

import Link from "next/link"
import { Plus, FileText, CheckCircle, Clock, AlertCircle, TrendingUp, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"

const stats = [
  {
    title: "Total Invoices",
    value: "1,234",
    change: "+12%",
    icon: FileText,
    trend: "up"
  },
  {
    title: "Processed Today",
    value: "23",
    change: "+5%",
    icon: CheckCircle,
    trend: "up"
  },
  {
    title: "Pending",
    value: "8",
    change: "-2%",
    icon: Clock,
    trend: "down"
  },
  {
    title: "Success Rate",
    value: "98.5%",
    change: "+0.5%",
    icon: TrendingUp,
    trend: "up"
  }
]

const recentInvoices = [
  {
    id: "INV-001",
    customer: "Acme Corporation",
    amount: "€1,250.00",
    status: "completed",
    date: "2024-01-15",
    type: "Factur-X"
  },
  {
    id: "INV-002",
    customer: "Tech Solutions Ltd",
    amount: "€850.00",
    status: "processing",
    date: "2024-01-15",
    type: "Standard PDF"
  },
  {
    id: "INV-003",
    customer: "Global Industries",
    amount: "€2,100.00",
    status: "completed",
    date: "2024-01-14",
    type: "Factur-X"
  },
  {
    id: "INV-004",
    customer: "StartUp Inc",
    amount: "€450.00",
    status: "failed",
    date: "2024-01-14",
    type: "Factur-X"
  },
  {
    id: "INV-005",
    customer: "Enterprise Corp",
    amount: "€3,200.00",
    status: "completed",
    date: "2024-01-13",
    type: "Factur-X"
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

export default function DashboardPage() {
  return (
    <div className="container px-4 py-8 mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here&apos;s an overview of your invoice activity.
          </p>
        </div>
        <Button asChild>
          <Link href="/invoices/new">
            <Plus className="mr-2 h-4 w-4" />
            Create Invoice
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className={`text-xs ${
                  stat.trend === "up" ? "text-green-600" : "text-red-600"
                }`}>
                  {stat.change} from last month
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        {/* Recent Invoices */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Invoices</CardTitle>
                <CardDescription>
                  Your latest invoice processing activity
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link href="/invoices">
                  View All
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentInvoices.map((invoice, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(invoice.status)}
                      <div>
                        <p className="font-medium">{invoice.id}</p>
                        <p className="text-sm text-muted-foreground">{invoice.customer}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="font-medium">{invoice.amount}</p>
                      <p className="text-sm text-muted-foreground">{invoice.date}</p>
                    </div>
                    <Badge className={getStatusColor(invoice.status)}>
                      {invoice.status}
                    </Badge>
                    <Button variant="ghost" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions & Usage */}
        <div className="space-y-8">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common tasks and shortcuts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/invoices/new">
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Invoice
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/invoices">
                  <FileText className="mr-2 h-4 w-4" />
                  View All Invoices
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/settings">
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Validation Settings
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Usage Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Monthly Usage</CardTitle>
              <CardDescription>
                Your current plan usage
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Invoices Created</span>
                  <span>23/500</span>
                </div>
                <Progress value={4.6} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>API Calls</span>
                  <span>1,234/10,000</span>
                </div>
                <Progress value={12.34} className="h-2" />
              </div>
              <div className="pt-2">
                <Button variant="outline" size="sm" className="w-full" asChild>
                  <Link href="/pricing">
                    Upgrade Plan
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}