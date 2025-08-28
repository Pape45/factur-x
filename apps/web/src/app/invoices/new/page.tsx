"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Plus, Trash2, Save, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"

interface InvoiceItem {
  id: string
  description: string
  quantity: number
  unitPrice: number
  vatRate: number
  total: number
}

interface InvoiceData {
  // Customer Information
  customerName: string
  customerEmail: string
  customerAddress: string
  customerCity: string
  customerPostalCode: string
  customerCountry: string
  customerVatNumber: string
  
  // Invoice Details
  invoiceNumber: string
  invoiceDate: string
  dueDate: string
  currency: string
  
  // Items
  items: InvoiceItem[]
  
  // Notes
  notes: string
  
  // Settings
  invoiceType: "facturx" | "standard"
}

const initialInvoiceData: InvoiceData = {
  customerName: "",
  customerEmail: "",
  customerAddress: "",
  customerCity: "",
  customerPostalCode: "",
  customerCountry: "France",
  customerVatNumber: "",
  invoiceNumber: "",
  invoiceDate: new Date().toISOString().split('T')[0],
  dueDate: "",
  currency: "EUR",
  items: [{
    id: "1",
    description: "",
    quantity: 1,
    unitPrice: 0,
    vatRate: 20,
    total: 0
  }],
  notes: "",
  invoiceType: "facturx"
}

export default function NewInvoicePage() {
  const router = useRouter()
  const [invoiceData, setInvoiceData] = useState<InvoiceData>(initialInvoiceData)
  const [isLoading, setIsLoading] = useState(false)

  const updateInvoiceData = (field: keyof InvoiceData, value: string | InvoiceItem[]) => {
    setInvoiceData(prev => ({ ...prev, [field]: value }))
  }

  const addItem = () => {
    const newItem: InvoiceItem = {
      id: Date.now().toString(),
      description: "",
      quantity: 1,
      unitPrice: 0,
      vatRate: 20,
      total: 0
    }
    setInvoiceData(prev => ({
      ...prev,
      items: [...prev.items, newItem]
    }))
  }

  const removeItem = (itemId: string) => {
    setInvoiceData(prev => ({
      ...prev,
      items: prev.items.filter(item => item.id !== itemId)
    }))
  }

  const updateItem = (itemId: string, field: keyof InvoiceItem, value: string | number) => {
    setInvoiceData(prev => ({
      ...prev,
      items: prev.items.map(item => {
        if (item.id === itemId) {
          const updatedItem = { ...item, [field]: value }
          // Recalculate total when quantity, unitPrice, or vatRate changes
          if (field === 'quantity' || field === 'unitPrice' || field === 'vatRate') {
            const subtotal = updatedItem.quantity * updatedItem.unitPrice
            updatedItem.total = subtotal * (1 + updatedItem.vatRate / 100)
          }
          return updatedItem
        }
        return item
      })
    }))
  }

  const calculateSubtotal = () => {
    return invoiceData.items.reduce((sum, item) => {
      return sum + (item.quantity * item.unitPrice)
    }, 0)
  }

  const calculateVAT = () => {
    return invoiceData.items.reduce((sum, item) => {
      const subtotal = item.quantity * item.unitPrice
      return sum + (subtotal * item.vatRate / 100)
    }, 0)
  }

  const calculateTotal = () => {
    return calculateSubtotal() + calculateVAT()
  }

  const handleSaveDraft = async () => {
    setIsLoading(true)
    // TODO: Implement save draft functionality
    console.log('Saving draft:', invoiceData)
    setTimeout(() => {
      setIsLoading(false)
      // Show success message
    }, 1000)
  }

  const handleGenerateInvoice = async () => {
    setIsLoading(true)
    // TODO: Implement invoice generation
    console.log('Generating invoice:', invoiceData)
    setTimeout(() => {
      setIsLoading(false)
      router.push('/invoices')
    }, 2000)
  }

  return (
    <div className="container px-4 py-8 mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Create New Invoice</h1>
          <p className="text-muted-foreground">
            Generate a new {invoiceData.invoiceType === 'facturx' ? 'Factur-X compliant' : 'standard PDF'} invoice
          </p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-8">
          {/* Invoice Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Invoice Settings</CardTitle>
              <CardDescription>
                Configure the basic invoice settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="invoiceType">Invoice Type</Label>
                  <Select
                    value={invoiceData.invoiceType}
                    onValueChange={(value: "facturx" | "standard") => updateInvoiceData('invoiceType', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="facturx">Factur-X (Recommended)</SelectItem>
                      <SelectItem value="standard">Standard PDF</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="currency">Currency</Label>
                  <Select
                    value={invoiceData.currency}
                    onValueChange={(value) => updateInvoiceData('currency', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="EUR">EUR (€)</SelectItem>
                      <SelectItem value="USD">USD ($)</SelectItem>
                      <SelectItem value="GBP">GBP (£)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="invoiceNumber">Invoice Number</Label>
                  <Input
                    id="invoiceNumber"
                    placeholder="INV-001"
                    value={invoiceData.invoiceNumber}
                    onChange={(e) => updateInvoiceData('invoiceNumber', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="invoiceDate">Invoice Date</Label>
                  <Input
                    id="invoiceDate"
                    type="date"
                    value={invoiceData.invoiceDate}
                    onChange={(e) => updateInvoiceData('invoiceDate', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dueDate">Due Date</Label>
                  <Input
                    id="dueDate"
                    type="date"
                    value={invoiceData.dueDate}
                    onChange={(e) => updateInvoiceData('dueDate', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Customer Information */}
          <Card>
            <CardHeader>
              <CardTitle>Customer Information</CardTitle>
              <CardDescription>
                Enter the billing details for your customer
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="customerName">Customer Name *</Label>
                  <Input
                    id="customerName"
                    placeholder="Acme Corporation"
                    value={invoiceData.customerName}
                    onChange={(e) => updateInvoiceData('customerName', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="customerEmail">Email Address</Label>
                  <Input
                    id="customerEmail"
                    type="email"
                    placeholder="contact@acme.com"
                    value={invoiceData.customerEmail}
                    onChange={(e) => updateInvoiceData('customerEmail', e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="customerAddress">Address *</Label>
                <Input
                  id="customerAddress"
                  placeholder="123 Business Street"
                  value={invoiceData.customerAddress}
                  onChange={(e) => updateInvoiceData('customerAddress', e.target.value)}
                  required
                />
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="customerCity">City *</Label>
                  <Input
                    id="customerCity"
                    placeholder="Paris"
                    value={invoiceData.customerCity}
                    onChange={(e) => updateInvoiceData('customerCity', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="customerPostalCode">Postal Code *</Label>
                  <Input
                    id="customerPostalCode"
                    placeholder="75001"
                    value={invoiceData.customerPostalCode}
                    onChange={(e) => updateInvoiceData('customerPostalCode', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="customerCountry">Country *</Label>
                  <Select
                    value={invoiceData.customerCountry}
                    onValueChange={(value) => updateInvoiceData('customerCountry', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="France">France</SelectItem>
                      <SelectItem value="Germany">Germany</SelectItem>
                      <SelectItem value="Spain">Spain</SelectItem>
                      <SelectItem value="Italy">Italy</SelectItem>
                      <SelectItem value="Netherlands">Netherlands</SelectItem>
                      <SelectItem value="Belgium">Belgium</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="customerVatNumber">VAT Number</Label>
                <Input
                  id="customerVatNumber"
                  placeholder="FR12345678901"
                  value={invoiceData.customerVatNumber}
                  onChange={(e) => updateInvoiceData('customerVatNumber', e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Invoice Items */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Invoice Items</CardTitle>
                  <CardDescription>
                    Add products or services to your invoice
                  </CardDescription>
                </div>
                <Button onClick={addItem} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Item
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {invoiceData.items.map((item, index) => (
                  <div key={item.id} className="p-4 border rounded-lg space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">Item {index + 1}</h4>
                      {invoiceData.items.length > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeItem(item.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="md:col-span-2 space-y-2">
                        <Label>Description *</Label>
                        <Textarea
                          placeholder="Product or service description"
                          value={item.description}
                          onChange={(e) => updateItem(item.id, 'description', e.target.value)}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Quantity *</Label>
                        <Input
                          type="number"
                          min="1"
                          step="1"
                          value={item.quantity}
                          onChange={(e) => updateItem(item.id, 'quantity', parseInt(e.target.value) || 1)}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Unit Price ({invoiceData.currency}) *</Label>
                        <Input
                          type="number"
                          min="0"
                          step="0.01"
                          value={item.unitPrice}
                          onChange={(e) => updateItem(item.id, 'unitPrice', parseFloat(e.target.value) || 0)}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>VAT Rate (%)</Label>
                        <Select
                          value={item.vatRate.toString()}
                          onValueChange={(value) => updateItem(item.id, 'vatRate', parseInt(value))}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="0">0% (Exempt)</SelectItem>
                            <SelectItem value="5.5">5.5% (Reduced)</SelectItem>
                            <SelectItem value="10">10% (Intermediate)</SelectItem>
                            <SelectItem value="20">20% (Standard)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Total ({invoiceData.currency})</Label>
                        <Input
                          value={item.total.toFixed(2)}
                          disabled
                          className="bg-muted"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Notes */}
          <Card>
            <CardHeader>
              <CardTitle>Additional Notes</CardTitle>
              <CardDescription>
                Add any additional information or terms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Payment terms, additional information, etc."
                value={invoiceData.notes}
                onChange={(e) => updateInvoiceData('notes', e.target.value)}
                rows={4}
              />
            </CardContent>
          </Card>
        </div>

        {/* Summary Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Invoice Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Subtotal:</span>
                  <span>{calculateSubtotal().toFixed(2)} {invoiceData.currency}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>VAT:</span>
                  <span>{calculateVAT().toFixed(2)} {invoiceData.currency}</span>
                </div>
                <Separator />
                <div className="flex justify-between font-medium">
                  <span>Total:</span>
                  <span>{calculateTotal().toFixed(2)} {invoiceData.currency}</span>
                </div>
              </div>
              
              <div className="pt-4 space-y-2">
                <Badge variant="outline" className="w-full justify-center">
                  {invoiceData.invoiceType === 'facturx' ? 'Factur-X Compliant' : 'Standard PDF'}
                </Badge>
                <p className="text-xs text-muted-foreground text-center">
                  {invoiceData.invoiceType === 'facturx' 
                    ? 'This invoice will include embedded XML data for automated processing'
                    : 'This will generate a standard PDF invoice'
                  }
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                onClick={handleSaveDraft} 
                variant="outline" 
                className="w-full"
                disabled={isLoading}
              >
                <Save className="h-4 w-4 mr-2" />
                Save as Draft
              </Button>
              <Button 
                onClick={handleGenerateInvoice} 
                className="w-full"
                disabled={isLoading || !invoiceData.customerName || !invoiceData.customerAddress}
              >
                <Send className="h-4 w-4 mr-2" />
                {isLoading ? 'Generating...' : 'Generate Invoice'}
              </Button>
              <p className="text-xs text-muted-foreground text-center">
                * Required fields must be completed
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}