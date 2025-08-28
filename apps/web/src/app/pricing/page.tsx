import Link from "next/link"
import { Check, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const plans = [
  {
    name: "Starter",
    price: "Free",
    description: "Perfect for small businesses getting started with Factur-X",
    features: [
      "Up to 10 invoices per month",
      "Basic Factur-X generation",
      "PDF/A-3 validation",
      "Email support",
      "Standard templates"
    ],
    cta: "Get Started",
    popular: false
  },
  {
    name: "Professional",
    price: "€29",
    description: "Ideal for growing businesses with higher volume needs",
    features: [
      "Up to 500 invoices per month",
      "Advanced Factur-X features",
      "Custom branding",
      "Priority support",
      "API access",
      "Bulk processing",
      "Advanced validation"
    ],
    cta: "Start Free Trial",
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large organizations with custom requirements",
    features: [
      "Unlimited invoices",
      "White-label solution",
      "Dedicated support",
      "Custom integrations",
      "SLA guarantee",
      "On-premise deployment",
      "Advanced analytics",
      "Custom workflows"
    ],
    cta: "Contact Sales",
    popular: false
  }
]

const faqs = [
  {
    question: "What is Factur-X?",
    answer: "Factur-X is a European standard for electronic invoicing that combines a PDF invoice with structured XML data, ensuring both human readability and machine processing capabilities."
  },
  {
    question: "Is there a free trial?",
    answer: "Yes! Our Professional plan comes with a 14-day free trial. No credit card required to get started."
  },
  {
    question: "Can I upgrade or downgrade my plan?",
    answer: "Absolutely! You can change your plan at any time. Upgrades take effect immediately, while downgrades take effect at the next billing cycle."
  },
  {
    question: "Do you offer custom enterprise solutions?",
    answer: "Yes, we provide custom enterprise solutions including on-premise deployment, custom integrations, and dedicated support. Contact our sales team for more information."
  }
]

export default function PricingPage() {
  return (
    <div className="container px-4 py-24 mx-auto">
      {/* Header */}
      <div className="text-center space-y-4 mb-16">
        <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl">
          Simple, Transparent Pricing
        </h1>
        <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
          Choose the perfect plan for your business. All plans include core Factur-X functionality.
        </p>
      </div>

      {/* Pricing Cards */}
      <div className="grid gap-8 md:grid-cols-3 mb-24">
        {plans.map((plan, index) => (
          <Card key={index} className={`relative ${plan.popular ? 'border-primary shadow-lg scale-105' : ''}`}>
            {plan.popular && (
              <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                Most Popular
              </Badge>
            )}
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <div className="space-y-2">
                <div className="text-4xl font-bold">
                  {plan.price}
                  {plan.price !== "Free" && plan.price !== "Custom" && (
                    <span className="text-lg font-normal text-muted-foreground">/month</span>
                  )}
                </div>
                <CardDescription className="text-base">
                  {plan.description}
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <ul className="space-y-3">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center space-x-3">
                    <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button 
                className="w-full" 
                variant={plan.popular ? "default" : "outline"}
                asChild
              >
                <Link href={plan.name === "Enterprise" ? "/contact" : "/dashboard"}>
                  {plan.cta}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">
            Frequently Asked Questions
          </h2>
          <p className="mx-auto max-w-[600px] text-gray-500 md:text-lg dark:text-gray-400">
            Everything you need to know about our pricing and plans.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {faqs.map((faq, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="text-lg">{faq.question}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{faq.answer}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center space-y-8 mt-24">
        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">
          Ready to Get Started?
        </h2>
        <p className="mx-auto max-w-[600px] text-gray-500 md:text-lg dark:text-gray-400">
          Join thousands of businesses already using Factur-X Express for their invoicing needs.
        </p>
        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Button size="lg" asChild>
            <Link href="/dashboard">
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
          <Button variant="outline" size="lg" asChild>
            <Link href="/contact">
              Contact Sales
            </Link>
          </Button>
        </div>
      </div>
    </div>
  )
}