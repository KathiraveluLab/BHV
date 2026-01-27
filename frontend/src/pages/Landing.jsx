import { Link } from 'react-router-dom';
import { Button } from '../components/Button';
import { ArrowRight, Shield, Heart, Lock } from 'lucide-react';

export function Landing() {
  return (
    <div className="bg-white">
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
          <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" style={{clipPath: "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)"}}></div>
        </div>
        
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56 text-center">
          <div className="hidden sm:mb-8 sm:flex sm:justify-center">
            <div className="relative rounded-full px-3 py-1 text-sm leading-6 text-slate-600 ring-1 ring-slate-900/10 hover:ring-slate-900/20">
              Prototype for GSoC Preparation. <a href="#features" className="font-semibold text-brand-600"><span className="absolute inset-0" aria-hidden="true"></span>Read more <ArrowRight className="inline-block h-3 w-3 ml-1" /></a>
            </div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
            Behavioral Health Vault
          </h1>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            A secure, calming space to document your journey. Store images and narratives in a private, local-first environment designed for mental wellness.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link to="/signup">
              <Button size="lg" className="px-8 py-3 text-base">
                Get started
              </Button>
            </Link>
            <Link to="/login">
                <span className="text-sm font-semibold leading-6 text-slate-900 flex items-center">
                Log in <ArrowRight className="h-4 w-4 ml-1" />
                </span>
            </Link>
          </div>
        </div>
      </div>

      <div id="features" className="mx-auto max-w-7xl px-6 lg:px-8 pb-24">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-brand-600">Secure & Private</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Everything you need to track your progress
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3">
            <div className="relative pl-16">
              <dt className="text-base font-semibold leading-7 text-slate-900">
                <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600">
                  <Lock className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                Secure Auth
              </dt>
              <dd className="mt-2 text-base leading-7 text-slate-600">
                Industry standard encryption and JWT authentication to keep your data safe.
              </dd>
            </div>
            <div className="relative pl-16">
              <dt className="text-base font-semibold leading-7 text-slate-900">
                <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600">
                  <Shield className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                Private Gallery
              </dt>
              <dd className="mt-2 text-base leading-7 text-slate-600">
                Upload images and stories that are only accessible to you.
              </dd>
            </div>
            <div className="relative pl-16">
              <dt className="text-base font-semibold leading-7 text-slate-900">
                <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600">
                  <Heart className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                Wellness Focused
              </dt>
              <dd className="mt-2 text-base leading-7 text-slate-600">
                Designed with calming colors and simple interactions to reduce cognitive load.
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}
