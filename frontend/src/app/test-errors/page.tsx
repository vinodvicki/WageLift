'use client';

import { useState } from 'react';
import { CrashProofForm } from '@/components/forms/crash-proof-form';
import { useToastHelpers } from '@/components/ui/toast';
import { Skeleton, SkeletonCard, SkeletonTable, SkeletonForm } from '@/components/ui/skeleton';
import { AlertCircle, Bug, Loader2, Save } from 'lucide-react';

export default function TestErrorsPage() {
  const toast = useToastHelpers();
  const [throwError, setThrowError] = useState(false);
  const [showSkeletons, setShowSkeletons] = useState(false);

  // This will trigger the error boundary
  if (throwError) {
    throw new Error('Test error boundary - This is intentional!');
  }

  const handleTestToasts = () => {
    toast.success('Success Toast', 'This is a success message');
    setTimeout(() => {
      toast.error('Error Toast', 'This is an error message');
    }, 1000);
    setTimeout(() => {
      toast.warning('Warning Toast', 'This is a warning message');
    }, 2000);
    setTimeout(() => {
      toast.info('Info Toast', 'This is an info message');
    }, 3000);
  };

  const handleTestPromiseToast = async () => {
    await toast.promise(
      new Promise((resolve) => setTimeout(resolve, 3000)),
      {
        loading: 'Processing...',
        success: () => 'Operation completed!',
        error: () => 'Operation failed!',
      }
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-gray-900">Error Handling Test Page</h1>
        
        {/* Error Boundary Test */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Bug className="h-5 w-5 mr-2" />
            Error Boundary Test
          </h2>
          <p className="text-gray-600 mb-4">
            Click the button below to trigger an error and see the error boundary in action.
          </p>
          <button
            onClick={() => setThrowError(true)}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Trigger Error Boundary
          </button>
        </section>

        {/* Toast Notifications Test */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            Toast Notifications Test
          </h2>
          <div className="space-y-4">
            <div>
              <button
                onClick={handleTestToasts}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mr-4"
              >
                Test All Toast Types
              </button>
              <button
                onClick={handleTestPromiseToast}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
              >
                Test Promise Toast
              </button>
            </div>
          </div>
        </section>

        {/* Crash-Proof Form Test */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Save className="h-5 w-5 mr-2" />
            Crash-Proof Form Test
          </h2>
          <p className="text-gray-600 mb-4">
            This form auto-saves every 5 seconds. Try filling it out and refreshing the page!
          </p>
          <CrashProofForm
            storageKey="test-form"
            initialValues={{
              name: '',
              email: '',
              message: '',
            }}
            validate={(values) => {
              const errors: Record<string, string> = {};
              if (!values['name']) errors['name'] = 'Name is required';
              if (!values['email']) errors['email'] = 'Email is required';
              if (values['email'] && !values['email'].includes('@')) {
                errors['email'] = 'Invalid email address';
              }
              if (!values['message']) errors['message'] = 'Message is required';
              return errors;
            }}
            onSubmit={async (values) => {
              // Simulate API call
              await new Promise((resolve, reject) => {
                setTimeout(() => {
                  if (Math.random() > 0.5) {
                    resolve(true);
                  } else {
                    reject(new Error('Random API failure for testing'));
                  }
                }, 2000);
              });
              console.log('Form submitted:', values);
            }}
          >
            {({ values, errors, touched, isSubmitting, isDirty, setValue, handleSubmit }) => (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Name {isDirty && <span className="text-green-600 text-xs">(unsaved)</span>}
                  </label>
                  <input
                    type="text"
                    value={values['name']}
                    onChange={(e) => setValue('name', e.target.value)}
                    className={`mt-1 block w-full rounded-md border ${
                      errors['name'] && touched['name']
                        ? 'border-red-300'
                        : 'border-gray-300'
                    } px-3 py-2`}
                  />
                  {errors['name'] && touched['name'] && (
                    <p className="mt-1 text-sm text-red-600">{errors['name']}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <input
                    type="email"
                    value={values['email']}
                    onChange={(e) => setValue('email', e.target.value)}
                    className={`mt-1 block w-full rounded-md border ${
                      errors['email'] && touched['email']
                        ? 'border-red-300'
                        : 'border-gray-300'
                    } px-3 py-2`}
                  />
                  {errors['email'] && touched['email'] && (
                    <p className="mt-1 text-sm text-red-600">{errors['email']}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Message
                  </label>
                  <textarea
                    value={values['message']}
                    onChange={(e) => setValue('message', e.target.value)}
                    rows={4}
                    className={`mt-1 block w-full rounded-md border ${
                      errors['message'] && touched['message']
                        ? 'border-red-300'
                        : 'border-gray-300'
                    } px-3 py-2`}
                  />
                  {errors['message'] && touched['message'] && (
                    <p className="mt-1 text-sm text-red-600">{errors['message']}</p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    'Submit (50% chance of failure for testing)'
                  )}
                </button>
              </form>
            )}
          </CrashProofForm>
        </section>

        {/* Skeleton Loading Test */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">
            Skeleton Loading States
          </h2>
          <button
            onClick={() => setShowSkeletons(!showSkeletons)}
            className="mb-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            {showSkeletons ? 'Hide' : 'Show'} Skeletons
          </button>
          
          {showSkeletons && (
            <div className="space-y-6">
              <div>
                <h3 className="font-medium mb-2">Basic Skeleton</h3>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4 mt-2" />
                <Skeleton className="h-4 w-1/2 mt-2" />
              </div>
              
              <div>
                <h3 className="font-medium mb-2">Skeleton Card</h3>
                <SkeletonCard />
              </div>
              
              <div>
                <h3 className="font-medium mb-2">Skeleton Table</h3>
                <SkeletonTable rows={3} />
              </div>
              
              <div>
                <h3 className="font-medium mb-2">Skeleton Form</h3>
                <SkeletonForm />
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}