import { getAccessToken, withApiAuthRequired } from '@auth0/nextjs-auth0'
import { NextRequest, NextResponse } from 'next/server'

export const GET = withApiAuthRequired(async function handler(req: NextRequest) {
  try {
    const res = new NextResponse()
    const { accessToken } = await getAccessToken(req, res, {
      scopes: ['openid', 'profile', 'email']
    })

    return NextResponse.json({ 
      accessToken,
      success: true 
    })
  } catch (error: any) {
    console.error('Token access error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to get access token',
        message: error.message 
      },
      { status: 500 }
    )
  }
}) 