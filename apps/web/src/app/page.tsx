import Link from "next/link"
import { ArrowRight, CheckCircle, FileText, Zap, Shield } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const features = [
  {
    icon: FileText,
    title: "Factur-X Compliant",
    description: "Generate fully compliant Factur-X invoices with embedded XML data according to European standards."
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Process invoices in seconds with our optimized FastAPI backend and modern architecture."
  },
  {
    icon: Shield,
    title: "Secure & Reliable",
    description: "Enterprise-grade security with JWT authentication and comprehensive validation."
  }
]

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="container px-4 py-24 mx-auto lg:py-32">
        <div className="flex flex-col items-center text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
              Professional
              <span className="text-primary"> Factur-X </span>
              Invoice Generation
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
              Create, validate, and manage Factur-X compliant invoices with ease. 
              Our platform ensures full compliance with European e-invoicing standards.
            </p>
          </div>
          <div className="flex flex-col gap-4 sm:flex-row">
            <Button asChild size="lg" className="text-lg px-8">
              <Link href="/dashboard">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8" asChild>
              <Link href="/pricing">
                View Pricing
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container px-4 py-24 mx-auto">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Why Choose Factur-X Express?
          </h2>
          <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
            Built with modern technology stack for maximum performance and reliability.
          </p>
        </div>
        <div className="grid gap-8 md:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="text-center">
                <CardHeader>
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-muted/50 py-24">
        <div className="container px-4 mx-auto">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-24 items-center">
            <div className="space-y-6">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">
                Streamline Your Invoice Process
              </h2>
              <p className="text-gray-500 md:text-lg dark:text-gray-400">
                Transform your invoicing workflow with our comprehensive Factur-X solution. 
                From generation to validation, we handle the complexity so you can focus on your business.
              </p>
              <ul className="space-y-4">
                {[
                  "Automatic XML CII generation",
                  "PDF/A-3 compliance validation",
                  "Real-time invoice processing",
                  "Comprehensive error handling"
                ].map((benefit, index) => (
                  <li key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="lg:order-first">
              <div className="aspect-square rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 p-8 flex items-center justify-center">
                <FileText className="h-32 w-32 text-primary" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container px-4 py-24 mx-auto">
        <div className="text-center space-y-8">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Ready to Get Started?
          </h2>
          <p className="mx-auto max-w-[600px] text-gray-500 md:text-xl dark:text-gray-400">
            Join thousands of businesses already using Factur-X Express for their invoicing needs.
          </p>
          <Button asChild size="lg" className="text-lg px-8">
            <Link href="/dashboard">
              Start Creating Invoices
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
