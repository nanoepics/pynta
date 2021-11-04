use dcam4_sys::*;
use std::convert::TryFrom;
pub mod dcam{
    #[derive(Copy,Clone,Debug)]
    #[repr(i32)]
    pub enum PixelType{
        None = dcam4_sys::DCAM_PIXELTYPE_DCAM_PIXELTYPE_NONE,
        Mono8 = dcam4_sys::DCAM_PIXELTYPE_DCAM_PIXELTYPE_MONO8,
        Mono16 = dcam4_sys::DCAM_PIXELTYPE_DCAM_PIXELTYPE_MONO16
    }

    impl std::convert::TryFrom<dcam4_sys::DCAM_PIXELTYPE> for PixelType{
        type Error = dcam4_sys::DCAM_PIXELTYPE;
        fn try_from(value: dcam4_sys::DCAM_PIXELTYPE) -> Result<Self, Self::Error> {
            match value {
                dcam4_sys::DCAM_PIXELTYPE_DCAM_PIXELTYPE_NONE => Ok(PixelType::None),
                dcam4_sys::DCAM_PIXELTYPE_DCAM_PIXELTYPE_MONO8 => Ok(PixelType::Mono8),
                dcam4_sys::DCAM_PIXELTYPE_DCAM_PIXELTYPE_MONO16 => Ok(PixelType::Mono16),
                x => Err(x)
            }
        }
    }
    #[derive(Copy,Clone,Debug)]
    #[repr(i32)]
    pub enum Error{
	/* status error */
	Busy = dcam4_sys::DCAMERR_DCAMERR_BUSY,
	Notready = dcam4_sys::DCAMERR_DCAMERR_NOTREADY,
	Notstable = dcam4_sys::DCAMERR_DCAMERR_NOTSTABLE,
	Unstable = dcam4_sys::DCAMERR_DCAMERR_UNSTABLE,
	Notbusy = dcam4_sys::DCAMERR_DCAMERR_NOTBUSY,
	Excluded = dcam4_sys::DCAMERR_DCAMERR_EXCLUDED,
	Coolingtrouble = dcam4_sys::DCAMERR_DCAMERR_COOLINGTROUBLE,
	Notrigger = dcam4_sys::DCAMERR_DCAMERR_NOTRIGGER,
	TemperatureTrouble = dcam4_sys::DCAMERR_DCAMERR_TEMPERATURE_TROUBLE,
	Toofrequenttrigger = dcam4_sys::DCAMERR_DCAMERR_TOOFREQUENTTRIGGER,
	Abort = dcam4_sys::DCAMERR_DCAMERR_ABORT,
	Timeout = dcam4_sys::DCAMERR_DCAMERR_TIMEOUT,
	Lostframe = dcam4_sys::DCAMERR_DCAMERR_LOSTFRAME,
	MissingframeTrouble = dcam4_sys::DCAMERR_DCAMERR_MISSINGFRAME_TROUBLE,
	Invalidimage = dcam4_sys::DCAMERR_DCAMERR_INVALIDIMAGE,
	Noresource = dcam4_sys::DCAMERR_DCAMERR_NORESOURCE,
	Nomemory = dcam4_sys::DCAMERR_DCAMERR_NOMEMORY,
	Nomodule = dcam4_sys::DCAMERR_DCAMERR_NOMODULE,
	Nodriver = dcam4_sys::DCAMERR_DCAMERR_NODRIVER,
	Nocamera = dcam4_sys::DCAMERR_DCAMERR_NOCAMERA,
	Nograbber = dcam4_sys::DCAMERR_DCAMERR_NOGRABBER,
	Nocombination = dcam4_sys::DCAMERR_DCAMERR_NOCOMBINATION,
	Failopen = dcam4_sys::DCAMERR_DCAMERR_FAILOPEN,
	FramegrabberNeedsFirmwareupdate = dcam4_sys::DCAMERR_DCAMERR_FRAMEGRABBER_NEEDS_FIRMWAREUPDATE,
	Invalidmodule = dcam4_sys::DCAMERR_DCAMERR_INVALIDMODULE,
	Invalidcommport = dcam4_sys::DCAMERR_DCAMERR_INVALIDCOMMPORT,
	Failopenbus = dcam4_sys::DCAMERR_DCAMERR_FAILOPENBUS,
	Failopencamera = dcam4_sys::DCAMERR_DCAMERR_FAILOPENCAMERA,
	Deviceproblem = dcam4_sys::DCAMERR_DCAMERR_DEVICEPROBLEM,
	Invalidcamera = dcam4_sys::DCAMERR_DCAMERR_INVALIDCAMERA,
	Invalidhandle = dcam4_sys::DCAMERR_DCAMERR_INVALIDHANDLE,
	Invalidparam = dcam4_sys::DCAMERR_DCAMERR_INVALIDPARAM,
	Invalidvalue = dcam4_sys::DCAMERR_DCAMERR_INVALIDVALUE,
	Outofrange = dcam4_sys::DCAMERR_DCAMERR_OUTOFRANGE,
	Notwritable = dcam4_sys::DCAMERR_DCAMERR_NOTWRITABLE,
	Notreadable = dcam4_sys::DCAMERR_DCAMERR_NOTREADABLE,
	Invalidpropertyid = dcam4_sys::DCAMERR_DCAMERR_INVALIDPROPERTYID,
	Newapirequired = dcam4_sys::DCAMERR_DCAMERR_NEWAPIREQUIRED,
	Wronghandshake = dcam4_sys::DCAMERR_DCAMERR_WRONGHANDSHAKE,
	Noproperty = dcam4_sys::DCAMERR_DCAMERR_NOPROPERTY,
	Invalidchannel = dcam4_sys::DCAMERR_DCAMERR_INVALIDCHANNEL,
	Invalidview = dcam4_sys::DCAMERR_DCAMERR_INVALIDVIEW,
	Invalidsubarray = dcam4_sys::DCAMERR_DCAMERR_INVALIDSUBARRAY,
	Accessdeny = dcam4_sys::DCAMERR_DCAMERR_ACCESSDENY,
	Novaluetext = dcam4_sys::DCAMERR_DCAMERR_NOVALUETEXT,
	Wrongpropertyvalue = dcam4_sys::DCAMERR_DCAMERR_WRONGPROPERTYVALUE,
	Disharmony = dcam4_sys::DCAMERR_DCAMERR_DISHARMONY,
	Framebundleshouldbeoff = dcam4_sys::DCAMERR_DCAMERR_FRAMEBUNDLESHOULDBEOFF,
	Invalidframeindex = dcam4_sys::DCAMERR_DCAMERR_INVALIDFRAMEINDEX,
	Invalidsessionindex = dcam4_sys::DCAMERR_DCAMERR_INVALIDSESSIONINDEX,
	Nocorrectiondata = dcam4_sys::DCAMERR_DCAMERR_NOCORRECTIONDATA,
	Channeldependentvalue = dcam4_sys::DCAMERR_DCAMERR_CHANNELDEPENDENTVALUE,
	Viewdependentvalue = dcam4_sys::DCAMERR_DCAMERR_VIEWDEPENDENTVALUE,
	Nodevicebuffer = dcam4_sys::DCAMERR_DCAMERR_NODEVICEBUFFER,
	Requiredsnap = dcam4_sys::DCAMERR_DCAMERR_REQUIREDSNAP,
	Lesssystemmemory = dcam4_sys::DCAMERR_DCAMERR_LESSSYSTEMMEMORY,
	Notsupport = dcam4_sys::DCAMERR_DCAMERR_NOTSUPPORT,
	Failreadcamera = dcam4_sys::DCAMERR_DCAMERR_FAILREADCAMERA,
	Failwritecamera = dcam4_sys::DCAMERR_DCAMERR_FAILWRITECAMERA,
	Conflictcommport = dcam4_sys::DCAMERR_DCAMERR_CONFLICTCOMMPORT,
	OpticsUnplugged = dcam4_sys::DCAMERR_DCAMERR_OPTICS_UNPLUGGED,
	Failcalibration = dcam4_sys::DCAMERR_DCAMERR_FAILCALIBRATION,
	MismatchConfiguration = dcam4_sys::DCAMERR_DCAMERR_MISMATCH_CONFIGURATION,
	Invalidmember3 = dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_3,
	Invalidmember5 = dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_5,
	Invalidmember7 = dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_7,
	Invalidmember8 = dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_8,
	Invalidmember9 = dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_9,
	Failedopenrecfile = dcam4_sys::DCAMERR_DCAMERR_FAILEDOPENRECFILE,
	Invalidrechandle = dcam4_sys::DCAMERR_DCAMERR_INVALIDRECHANDLE,
	Failedwritedata = dcam4_sys::DCAMERR_DCAMERR_FAILEDWRITEDATA,
	Failedreaddata = dcam4_sys::DCAMERR_DCAMERR_FAILEDREADDATA,
	Nowrecording = dcam4_sys::DCAMERR_DCAMERR_NOWRECORDING,
	Writefull = dcam4_sys::DCAMERR_DCAMERR_WRITEFULL,
	Alreadyoccupied = dcam4_sys::DCAMERR_DCAMERR_ALREADYOCCUPIED,
	Toolargeuserdatasize = dcam4_sys::DCAMERR_DCAMERR_TOOLARGEUSERDATASIZE,
	Invalidwaithandle = dcam4_sys::DCAMERR_DCAMERR_INVALIDWAITHANDLE,
	Newruntimerequired = dcam4_sys::DCAMERR_DCAMERR_NEWRUNTIMEREQUIRED,
	Versionmismatch = dcam4_sys::DCAMERR_DCAMERR_VERSIONMISMATCH,
	RunasFactorymode = dcam4_sys::DCAMERR_DCAMERR_RUNAS_FACTORYMODE,
	ImageUnknownsignature = dcam4_sys::DCAMERR_DCAMERR_IMAGE_UNKNOWNSIGNATURE,
	ImageNewruntimerequired = dcam4_sys::DCAMERR_DCAMERR_IMAGE_NEWRUNTIMEREQUIRED,
	ImageErrorstatusexist = dcam4_sys::DCAMERR_DCAMERR_IMAGE_ERRORSTATUSEXIST,
	ImageHeadercorrupted = dcam4_sys::DCAMERR_DCAMERR_IMAGE_HEADERCORRUPTED,
	ImageBrokencontent = dcam4_sys::DCAMERR_DCAMERR_IMAGE_BROKENCONTENT,
	Unknownmsgid = dcam4_sys::DCAMERR_DCAMERR_UNKNOWNMSGID,
	Unknownstrid = dcam4_sys::DCAMERR_DCAMERR_UNKNOWNSTRID,
	Unknownparamid = dcam4_sys::DCAMERR_DCAMERR_UNKNOWNPARAMID,
	Unknownbitstype = dcam4_sys::DCAMERR_DCAMERR_UNKNOWNBITSTYPE,
	Unknowndatatype = dcam4_sys::DCAMERR_DCAMERR_UNKNOWNDATATYPE,
	None = dcam4_sys::DCAMERR_DCAMERR_NONE,
	Installationinprogress = dcam4_sys::DCAMERR_DCAMERR_INSTALLATIONINPROGRESS,
	Unreach = dcam4_sys::DCAMERR_DCAMERR_UNREACH,
	Unloaded = dcam4_sys::DCAMERR_DCAMERR_UNLOADED,
	Thruadapter = dcam4_sys::DCAMERR_DCAMERR_THRUADAPTER,
	Noconnection = dcam4_sys::DCAMERR_DCAMERR_NOCONNECTION,
	Notimplement = dcam4_sys::DCAMERR_DCAMERR_NOTIMPLEMENT,
	Delayedframe = dcam4_sys::DCAMERR_DCAMERR_DELAYEDFRAME,
	Deviceinitializing = dcam4_sys::DCAMERR_DCAMERR_DEVICEINITIALIZING,
	ApiinitInitoptionbytes = dcam4_sys::DCAMERR_DCAMERR_APIINIT_INITOPTIONBYTES,
	ApiinitInitoption = dcam4_sys::DCAMERR_DCAMERR_APIINIT_INITOPTION,
	InitoptionCollisionBase = dcam4_sys::DCAMERR_DCAMERR_INITOPTION_COLLISION_BASE,
	InitoptionCollisionMax = dcam4_sys::DCAMERR_DCAMERR_INITOPTION_COLLISION_MAX,
	MisspropTriggersource = dcam4_sys::DCAMERR_DCAMERR_MISSPROP_TRIGGERSOURCE,
	Success = dcam4_sys::DCAMERR_DCAMERR_SUCCESS,
	//for when the C api returns an error that we do not know exists.
	UnknownError
    }

	impl std::convert::TryFrom<dcam4_sys::DCAMERR> for Error{
		type Error = dcam4_sys::DCAMERR;
		fn try_from(value : dcam4_sys::DCAMERR) -> Result<Self, Self::Error> {
			match value{
				dcam4_sys::DCAMERR_DCAMERR_BUSY => Ok(Error::Busy),
				dcam4_sys::DCAMERR_DCAMERR_NOTREADY => Ok(Error::Notready),
				dcam4_sys::DCAMERR_DCAMERR_NOTSTABLE => Ok(Error::Notstable),
				dcam4_sys::DCAMERR_DCAMERR_UNSTABLE => Ok(Error::Unstable),
				dcam4_sys::DCAMERR_DCAMERR_NOTBUSY => Ok(Error::Notbusy),
				dcam4_sys::DCAMERR_DCAMERR_EXCLUDED => Ok(Error::Excluded),
				dcam4_sys::DCAMERR_DCAMERR_COOLINGTROUBLE => Ok(Error::Coolingtrouble),
				dcam4_sys::DCAMERR_DCAMERR_NOTRIGGER => Ok(Error::Notrigger),
				dcam4_sys::DCAMERR_DCAMERR_TEMPERATURE_TROUBLE => Ok(Error::TemperatureTrouble),
				dcam4_sys::DCAMERR_DCAMERR_TOOFREQUENTTRIGGER => Ok(Error::Toofrequenttrigger),
				dcam4_sys::DCAMERR_DCAMERR_ABORT => Ok(Error::Abort),
				dcam4_sys::DCAMERR_DCAMERR_TIMEOUT => Ok(Error::Timeout),
				dcam4_sys::DCAMERR_DCAMERR_LOSTFRAME => Ok(Error::Lostframe),
				dcam4_sys::DCAMERR_DCAMERR_MISSINGFRAME_TROUBLE => Ok(Error::MissingframeTrouble),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDIMAGE => Ok(Error::Invalidimage),
				dcam4_sys::DCAMERR_DCAMERR_NORESOURCE => Ok(Error::Noresource),
				dcam4_sys::DCAMERR_DCAMERR_NOMEMORY => Ok(Error::Nomemory),
				dcam4_sys::DCAMERR_DCAMERR_NOMODULE => Ok(Error::Nomodule),
				dcam4_sys::DCAMERR_DCAMERR_NODRIVER => Ok(Error::Nodriver),
				dcam4_sys::DCAMERR_DCAMERR_NOCAMERA => Ok(Error::Nocamera),
				dcam4_sys::DCAMERR_DCAMERR_NOGRABBER => Ok(Error::Nograbber),
				dcam4_sys::DCAMERR_DCAMERR_NOCOMBINATION => Ok(Error::Nocombination),
				dcam4_sys::DCAMERR_DCAMERR_FAILOPEN => Ok(Error::Failopen),
				dcam4_sys::DCAMERR_DCAMERR_FRAMEGRABBER_NEEDS_FIRMWAREUPDATE => Ok(Error::FramegrabberNeedsFirmwareupdate),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDMODULE => Ok(Error::Invalidmodule),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDCOMMPORT => Ok(Error::Invalidcommport),
				dcam4_sys::DCAMERR_DCAMERR_FAILOPENBUS => Ok(Error::Failopenbus),
				dcam4_sys::DCAMERR_DCAMERR_FAILOPENCAMERA => Ok(Error::Failopencamera),
				dcam4_sys::DCAMERR_DCAMERR_DEVICEPROBLEM => Ok(Error::Deviceproblem),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDCAMERA => Ok(Error::Invalidcamera),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDHANDLE => Ok(Error::Invalidhandle),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDPARAM => Ok(Error::Invalidparam),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDVALUE => Ok(Error::Invalidvalue),
				dcam4_sys::DCAMERR_DCAMERR_OUTOFRANGE => Ok(Error::Outofrange),
				dcam4_sys::DCAMERR_DCAMERR_NOTWRITABLE => Ok(Error::Notwritable),
				dcam4_sys::DCAMERR_DCAMERR_NOTREADABLE => Ok(Error::Notreadable),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDPROPERTYID => Ok(Error::Invalidpropertyid),
				dcam4_sys::DCAMERR_DCAMERR_NEWAPIREQUIRED => Ok(Error::Newapirequired),
				dcam4_sys::DCAMERR_DCAMERR_WRONGHANDSHAKE => Ok(Error::Wronghandshake),
				dcam4_sys::DCAMERR_DCAMERR_NOPROPERTY => Ok(Error::Noproperty),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDCHANNEL => Ok(Error::Invalidchannel),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDVIEW => Ok(Error::Invalidview),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDSUBARRAY => Ok(Error::Invalidsubarray),
				dcam4_sys::DCAMERR_DCAMERR_ACCESSDENY => Ok(Error::Accessdeny),
				dcam4_sys::DCAMERR_DCAMERR_NOVALUETEXT => Ok(Error::Novaluetext),
				dcam4_sys::DCAMERR_DCAMERR_WRONGPROPERTYVALUE => Ok(Error::Wrongpropertyvalue),
				dcam4_sys::DCAMERR_DCAMERR_DISHARMONY => Ok(Error::Disharmony),
				dcam4_sys::DCAMERR_DCAMERR_FRAMEBUNDLESHOULDBEOFF => Ok(Error::Framebundleshouldbeoff),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDFRAMEINDEX => Ok(Error::Invalidframeindex),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDSESSIONINDEX => Ok(Error::Invalidsessionindex),
				dcam4_sys::DCAMERR_DCAMERR_NOCORRECTIONDATA => Ok(Error::Nocorrectiondata),
				dcam4_sys::DCAMERR_DCAMERR_CHANNELDEPENDENTVALUE => Ok(Error::Channeldependentvalue),
				dcam4_sys::DCAMERR_DCAMERR_VIEWDEPENDENTVALUE => Ok(Error::Viewdependentvalue),
				dcam4_sys::DCAMERR_DCAMERR_NODEVICEBUFFER => Ok(Error::Nodevicebuffer),
				dcam4_sys::DCAMERR_DCAMERR_REQUIREDSNAP => Ok(Error::Requiredsnap),
				dcam4_sys::DCAMERR_DCAMERR_LESSSYSTEMMEMORY => Ok(Error::Lesssystemmemory),
				dcam4_sys::DCAMERR_DCAMERR_NOTSUPPORT => Ok(Error::Notsupport),
				dcam4_sys::DCAMERR_DCAMERR_FAILREADCAMERA => Ok(Error::Failreadcamera),
				dcam4_sys::DCAMERR_DCAMERR_FAILWRITECAMERA => Ok(Error::Failwritecamera),
				dcam4_sys::DCAMERR_DCAMERR_CONFLICTCOMMPORT => Ok(Error::Conflictcommport),
				dcam4_sys::DCAMERR_DCAMERR_OPTICS_UNPLUGGED => Ok(Error::OpticsUnplugged),
				dcam4_sys::DCAMERR_DCAMERR_FAILCALIBRATION => Ok(Error::Failcalibration),
				dcam4_sys::DCAMERR_DCAMERR_MISMATCH_CONFIGURATION => Ok(Error::MismatchConfiguration),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_3 => Ok(Error::Invalidmember3),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_5 => Ok(Error::Invalidmember5),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_7 => Ok(Error::Invalidmember7),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_8 => Ok(Error::Invalidmember8),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDMEMBER_9 => Ok(Error::Invalidmember9),
				dcam4_sys::DCAMERR_DCAMERR_FAILEDOPENRECFILE => Ok(Error::Failedopenrecfile),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDRECHANDLE => Ok(Error::Invalidrechandle),
				dcam4_sys::DCAMERR_DCAMERR_FAILEDWRITEDATA => Ok(Error::Failedwritedata),
				dcam4_sys::DCAMERR_DCAMERR_FAILEDREADDATA => Ok(Error::Failedreaddata),
				dcam4_sys::DCAMERR_DCAMERR_NOWRECORDING => Ok(Error::Nowrecording),
				dcam4_sys::DCAMERR_DCAMERR_WRITEFULL => Ok(Error::Writefull),
				dcam4_sys::DCAMERR_DCAMERR_ALREADYOCCUPIED => Ok(Error::Alreadyoccupied),
				dcam4_sys::DCAMERR_DCAMERR_TOOLARGEUSERDATASIZE => Ok(Error::Toolargeuserdatasize),
				dcam4_sys::DCAMERR_DCAMERR_INVALIDWAITHANDLE => Ok(Error::Invalidwaithandle),
				dcam4_sys::DCAMERR_DCAMERR_NEWRUNTIMEREQUIRED => Ok(Error::Newruntimerequired),
				dcam4_sys::DCAMERR_DCAMERR_VERSIONMISMATCH => Ok(Error::Versionmismatch),
				dcam4_sys::DCAMERR_DCAMERR_RUNAS_FACTORYMODE => Ok(Error::RunasFactorymode),
				dcam4_sys::DCAMERR_DCAMERR_IMAGE_UNKNOWNSIGNATURE => Ok(Error::ImageUnknownsignature),
				dcam4_sys::DCAMERR_DCAMERR_IMAGE_NEWRUNTIMEREQUIRED => Ok(Error::ImageNewruntimerequired),
				dcam4_sys::DCAMERR_DCAMERR_IMAGE_ERRORSTATUSEXIST => Ok(Error::ImageErrorstatusexist),
				dcam4_sys::DCAMERR_DCAMERR_IMAGE_HEADERCORRUPTED => Ok(Error::ImageHeadercorrupted),
				dcam4_sys::DCAMERR_DCAMERR_IMAGE_BROKENCONTENT => Ok(Error::ImageBrokencontent),
				dcam4_sys::DCAMERR_DCAMERR_UNKNOWNMSGID => Ok(Error::Unknownmsgid),
				dcam4_sys::DCAMERR_DCAMERR_UNKNOWNSTRID => Ok(Error::Unknownstrid),
				dcam4_sys::DCAMERR_DCAMERR_UNKNOWNPARAMID => Ok(Error::Unknownparamid),
				dcam4_sys::DCAMERR_DCAMERR_UNKNOWNBITSTYPE => Ok(Error::Unknownbitstype),
				dcam4_sys::DCAMERR_DCAMERR_UNKNOWNDATATYPE => Ok(Error::Unknowndatatype),
				dcam4_sys::DCAMERR_DCAMERR_NONE => Ok(Error::None),
				dcam4_sys::DCAMERR_DCAMERR_INSTALLATIONINPROGRESS => Ok(Error::Installationinprogress),
				dcam4_sys::DCAMERR_DCAMERR_UNREACH => Ok(Error::Unreach),
				dcam4_sys::DCAMERR_DCAMERR_UNLOADED => Ok(Error::Unloaded),
				dcam4_sys::DCAMERR_DCAMERR_THRUADAPTER => Ok(Error::Thruadapter),
				dcam4_sys::DCAMERR_DCAMERR_NOCONNECTION => Ok(Error::Noconnection),
				dcam4_sys::DCAMERR_DCAMERR_NOTIMPLEMENT => Ok(Error::Notimplement),
				dcam4_sys::DCAMERR_DCAMERR_DELAYEDFRAME => Ok(Error::Delayedframe),
				dcam4_sys::DCAMERR_DCAMERR_DEVICEINITIALIZING => Ok(Error::Deviceinitializing),
				dcam4_sys::DCAMERR_DCAMERR_APIINIT_INITOPTIONBYTES => Ok(Error::ApiinitInitoptionbytes),
				dcam4_sys::DCAMERR_DCAMERR_APIINIT_INITOPTION => Ok(Error::ApiinitInitoption),
				dcam4_sys::DCAMERR_DCAMERR_INITOPTION_COLLISION_BASE => Ok(Error::InitoptionCollisionBase),
				dcam4_sys::DCAMERR_DCAMERR_INITOPTION_COLLISION_MAX => Ok(Error::InitoptionCollisionMax),
				dcam4_sys::DCAMERR_DCAMERR_MISSPROP_TRIGGERSOURCE => Ok(Error::MisspropTriggersource),
				dcam4_sys::DCAMERR_DCAMERR_SUCCESS => Ok(Error::Success),
				e => Err(e)
			}
		}
	}
}


pub struct Camera{
    handle : dcam4_sys::HDCAM,
    // mode : CameraModel::CaptureMode,
    // image_buffer: Box<[u16]>
}

impl std::ops::Drop for Camera{
	fn drop(&mut self) {
		println!("closing device...");
		println!("{:?}", unsafe{dcam::Error::try_from(dcam4_sys::dcamdev_close(self.handle))});
	}
}

pub struct Image{
    metadata : DCAMBUF_FRAME,
    data : [u8]
}

#[derive(Debug)]
struct Api{
	api: dcam4_sys::DCAMAPI_INIT,
}

impl Api {
	pub fn init() -> Result<Self, dcam::Error>{
		let mut param = dcam4_sys::DCAMAPI_INIT{
			size : std::mem::size_of::<dcam4_sys::DCAMAPI_INIT>() as i32,
			iDeviceCount : 0,
			reserved : 0,
			initoptionbytes: 0,
			initoption : std::ptr::null(),
			guid: std::ptr::null()
		};
		match unsafe{dcam::Error::try_from(dcam4_sys::dcamapi_init(&mut param))} {
			Ok(dcam::Error::Success) => {
				println!("There are {} devices", param.iDeviceCount);
				Ok(Self{api : param})
			},
			Ok(e) => Err(e),
			Err(e) => Err(dcam::Error::UnknownError)
		}
	}
}

//Drop does not get called for statics. if we want to do this it's either explicit or via counting devices and the Camera drop whenever we drop the last active device.
// impl std::ops::Drop for Api{
// 	fn drop(&mut self) {
// 		println!("dropping API...");
// 		println!("{:?}", unsafe{dcam4_sys::dcamapi_uninit()});
// 	}
// }


//TODO(hayley): verify
unsafe impl Sync for Api{}
unsafe impl Send for Api{}
unsafe impl Sync for Camera{}
unsafe impl Send for Camera{}

use std::sync::RwLock;
use lazy_static::lazy_static;
lazy_static!{
	static ref API : RwLock<Option<Api>> = RwLock::new(None);
}
fn dcam_check(err : dcam4_sys::DCAMERR) -> Result<(),dcam::Error> {
	match dcam::Error::try_from(err) {
		Ok(dcam::Error::Success) => Ok(()),
		Ok(e) => Err(e),
		Err(_) => Err(dcam::Error::UnknownError)
	}
}

#[derive(Copy,Clone,Debug)]
pub enum Pixels<'a>{
    MonoU16(&'a [u16]),
    MonoU8(&'a [u8]),
}

impl Image{
    fn format(&self) -> dcam::PixelType{
        use std::convert::TryInto;
        self.metadata.type_.try_into().unwrap()
    }
    fn size(&self) -> (usize, usize) {
        //TODO(hayley): check signedness of metadata?
        (self.metadata.width as usize, self.metadata.height as usize)
    }
	fn pixels<'a>(&'a self) -> Pixels<'a> {
		match self.format() {
			dcam::PixelType::Mono8 => Pixels::MonoU8(&self.data),
			dcam::PixelType::Mono16 => Pixels::MonoU16(unsafe{
				std::slice::from_raw_parts(
					std::mem::transmute::<*const u8, *const u16>(self.data.as_ptr()),
					self.data.len()/2
				)}),
			_ => unreachable!()
		}
		
	}
}

impl Camera{
    pub fn new() -> Self{
		let dev_open = unsafe{
		if unsafe{API.read()}.expect("DCAM API lock got poisoned!").is_none() {
			let mut p = unsafe{API.write()}.expect("DCAM API lock got poisoned!");
			*p = Some(Api::init().expect("Failed to initialize DCAM api"));
		}
		let mut dev_open = dcam4_sys::DCAMDEV_OPEN {
			size : std::mem::size_of::<dcam4_sys::DCAMDEV_OPEN>() as i32,
			index : 0,
			hdcam : std::ptr::null_mut()
		};
		match dcam::Error::try_from(dcam4_sys::dcamdev_open(&mut dev_open)) {
			Ok(dcam::Error::Success) => (),
			_ => unreachable!()
		}
		// match dcam::Error::try_from(dcam4_sys::dcambuf_alloc(dev_open.hdcam, 1)) {
		// 	Ok(dcam::Error::Success) => (),
		// 	_ => unreachable!()
		// };
		dev_open
		};
        let ret = Self{
            handle : dev_open.hdcam,
        //     // mode : CameraModel::CaptureMode::SingleShot,
        //     // image_buffer :  unsafe{Box::<[u16]>::new_zeroed_slice(2048*2048).assume_init()}
		// 	// unsafe{
        //     //     let values = Box::<[u8]>::new_zeroed_slice(2048*2048*2+std::mem::size_of::<dcam4_sys::DCAMBUF_FRAME>());
        //     //     unsafe {
        //     //         let values = values.assume_init();
        //     //         Box::from_raw(std::mem::transmute::<&mut [u8], &mut Image>(Box::leak(values)))
        //     //     }
        //     // }
        };
		// unsafe{
		// let attach = dcam4_sys::DCAMBUF_ATTACH{
		// 	size : std::mem::size_of::<dcam4_sys::DCAMBUF_ATTACH>() as i32,
		// 	iKind : DCAM_ATTACHKIND_DCAMBUF_ATTACHKIND_FRAME,
		// 	buffer : &mut (std::mem::transmute::<&mut [u16], &mut [u8]>(&mut ret.image_buffer).as_mut_ptr_range().start as *mut _),
		// 	buffercount : 1
		// };
		// dcam_check(dcambuf_attach(ret.handle, &attach)).unwrap();
		// }
		ret
    }

    pub fn set_exposure(&mut self, exposure : std::time::Duration) -> Result<std::time::Duration, dcam::Error> { 
		//0.003020752 to 10.0
		Ok(std::time::Duration::from_secs_f64(self.set_get_property(_DCAMIDPROP_DCAM_IDPROP_EXPOSURETIME, exposure.as_secs_f64())?))
    }
    pub fn get_exposure(&self) -> Result<std::time::Duration, dcam::Error> { 
        Ok(std::time::Duration::from_secs_f64(self.get_property(_DCAMIDPROP_DCAM_IDPROP_EXPOSURETIME)?))
    }
	pub fn set_property(&self, property_id : i32, val : f64) -> Result<(), dcam::Error>{
		unsafe{dcam_check(dcam4_sys::dcamprop_setvalue(self.handle, property_id, val))}
	}
	pub fn set_get_property(&self, property_id : i32, mut val : f64) -> Result<f64, dcam::Error>{
		unsafe{dcam_check(dcam4_sys::dcamprop_setgetvalue(self.handle, property_id, &mut val, 0))?;}
		Ok(val)
	}
	pub fn get_property(&self, property_id : i32) -> Result<f64, dcam::Error>{
		let mut val = 0.0;
		unsafe{dcam_check(dcam4_sys::dcamprop_getvalue(self.handle, property_id, &mut val))?;}
		Ok(val)
	}
    pub fn set_region_of_interest(&mut self, x : (usize, usize), y: (usize, usize)) -> Result<(), dcam::Error>{

		self.set_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYHPOS, 0.0)?;
		self.set_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYVPOS, 0.0)?;
		//TODO(hayley): handle x1 > x0
		let vsize = ((x.1-x.0)/4)*4;
        let vpos = (x.0/4)*4;
        let hsize = ((y.1-y.0)/4)*4;
        let hpos = (y.0/4)*4;
		self.set_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYVSIZE, hsize as f64)?;
        self.set_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYHSIZE, vsize as f64)?;
        self.set_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYVPOS, hpos as f64)?;
        self.set_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYHPOS, vpos as f64)?;
		self.set_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYMODE, _DCAMPROPMODEVALUE_DCAMPROP_MODE__ON as f64)?;
		Ok(())
    }
    pub fn get_region_of_interest(&self) -> Result<((usize, usize), (usize, usize)), dcam::Error> {
        let vsize = self.get_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYVSIZE)? as usize;
		let hsize = self.get_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYHSIZE)? as usize;
		let hpos = self.get_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYHPOS)? as usize;
		let vpos = self.get_property(_DCAMIDPROP_DCAM_IDPROP_SUBARRAYVPOS)? as usize;
        Ok(((hpos, hpos+hsize), (vpos, vpos+vsize)))
    }

	fn get_bytes_per_frame(&self) -> Result<usize, dcam::Error> {
		Ok(self.get_property(_DCAMIDPROP_DCAM_IDPROP_BUFFER_FRAMEBYTES)? as usize)
	}
    // fn set_capture_mode(&mut self, mode: CameraModel::CaptureMode) {
    //     self.mode = mode;
    // }
    // fn get_capture_mode(&self) -> CameraModel::CaptureMode {
    //     self.mode
    // }
    // pub fn snap(&self) -> &[u16]{
		// unsafe{ 
		// dcam_check(dcam4_sys::dcamcap_start(self.handle, dcam4_sys::DCAMCAP_START_DCAMCAP_START_SNAP)).unwrap();
		// let mut wait_open = dcam4_sys::DCAMWAIT_OPEN{
		// 	size : std::mem::size_of::<dcam4_sys::DCAMWAIT_OPEN>() as i32,
		// 	supportevent : 0,
		// 	hwait : std::ptr::null_mut(),
		// 	hdcam : self.handle
		// };
		// dcam_check(dcam4_sys::dcamwait_open(&mut wait_open)).unwrap();
		// let mut wait = dcam4_sys::DCAMWAIT_START{
		// 	size : std::mem::size_of::<dcam4_sys::DCAMWAIT_START>() as i32,
		// 	eventhappened : 0,
		// 	eventmask : dcam4_sys::DCAMWAIT_EVENT_DCAMWAIT_CAPEVENT_FRAMEREADY,
		// 	timeout : DCAMWAIT_TIMEOUT_DCAMWAIT_TIMEOUT_INFINITE
		// };
		// dcam_check(dcam4_sys::dcamwait_start(wait_open.hwait, &mut wait)).unwrap();
		// }
	// 	//DCAMWAIT_CAPEVENT.FRAMEREADY, timeout_millisec
	// 	//dcamwait_start
	// 	//dcambuf_copyframe(...)
    //     // std::mem::transmute<&Image, &self.image_buffer.as_ref().pixels()
	// 	self.image_buffer.as_ref()
	// 	// unsafe{
	// 	// 	std::slice::from_raw_parts(
	// 	// 		std::mem::transmute::<*const u8, *const u16>(self.image_buffer.data.as_ptr()),
	// 	// 		self.image_buffer.data.len()/2
	// 	// 	)}
    // }
	

	pub fn snap_into(&mut self, data : &mut [u16]) -> Result<(), dcam::Error>{
		unsafe{
			dcam_check(dcam4_sys::dcambuf_release(self.handle, dcam4_sys::DCAM_ATTACHKIND_DCAMBUF_ATTACHKIND_FRAME))?;
			let attach = dcam4_sys::DCAMBUF_ATTACH{
				size : std::mem::size_of::<dcam4_sys::DCAMBUF_ATTACH>() as i32,
				iKind : DCAM_ATTACHKIND_DCAMBUF_ATTACHKIND_FRAME,
				buffer : &mut (std::mem::transmute::<&mut [u16], &mut [u8]>(data).as_mut_ptr_range().start as *mut _),
				buffercount : 1
			};
			dcam_check(dcambuf_attach(self.handle, &attach))?;
			dcam_check(dcam4_sys::dcamcap_start(self.handle, dcam4_sys::DCAMCAP_START_DCAMCAP_START_SNAP)).unwrap();
			let mut wait_open = dcam4_sys::DCAMWAIT_OPEN{
				size : std::mem::size_of::<dcam4_sys::DCAMWAIT_OPEN>() as i32,
				supportevent : 0,
				hwait : std::ptr::null_mut(),
				hdcam : self.handle
			};
			dcam_check(dcam4_sys::dcamwait_open(&mut wait_open)).unwrap();
			let mut wait = dcam4_sys::DCAMWAIT_START{
				size : std::mem::size_of::<dcam4_sys::DCAMWAIT_START>() as i32,
				eventhappened : 0,
				eventmask : dcam4_sys::DCAMWAIT_EVENT_DCAMWAIT_CAPEVENT_FRAMEREADY,
				timeout : DCAMWAIT_TIMEOUT_DCAMWAIT_TIMEOUT_INFINITE
			};
			dcam_check(dcam4_sys::dcamwait_start(wait_open.hwait, &mut wait)).unwrap();
			dcam_check(dcam4_sys::dcambuf_release(self.handle, dcam4_sys::DCAM_ATTACHKIND_DCAMBUF_ATTACHKIND_FRAME))?;
			dcam_check(dcam4_sys::dcamwait_close(wait_open.hwait))?
		}
		Ok(())
	}
	pub fn start_streaming_into(&mut self, data: &mut[&mut [u16]]) -> Result<(), dcam::Error>{
		unsafe{
			dcam_check(dcam4_sys::dcambuf_release(self.handle, dcam4_sys::DCAM_ATTACHKIND_DCAMBUF_ATTACHKIND_FRAME))?;
			let attach = dcam4_sys::DCAMBUF_ATTACH{
				size : std::mem::size_of::<dcam4_sys::DCAMBUF_ATTACH>() as i32,
				iKind : DCAM_ATTACHKIND_DCAMBUF_ATTACHKIND_FRAME,
				buffer : std::mem::transmute::<&mut[&mut [u16]], &mut[&mut [u8]]>(data).as_mut_ptr_range().start as *mut _,
				buffercount : 1
			};
			dcam_check(dcambuf_attach(self.handle, &attach))?;
			dcam_check(dcam4_sys::dcamcap_start(self.handle, dcam4_sys::DCAMCAP_START_DCAMCAP_START_SEQUENCE))?;
		}
		// unsafe{
		// 	let mut wait_open = dcam4_sys::DCAMWAIT_OPEN{
		// 		size : std::mem::size_of::<dcam4_sys::DCAMWAIT_OPEN>() as i32,
		// 		supportevent : 0,
		// 		hwait : std::ptr::null_mut(),
		// 		hdcam : self.handle
		// 	};
		// 	dcam_check(dcam4_sys::dcamwait_open(&mut wait_open))?;
		// 	let mut wait = dcam4_sys::DCAMWAIT_START{
		// 		size : std::mem::size_of::<dcam4_sys::DCAMWAIT_START>() as i32,
		// 		eventhappened : 0,
		// 		eventmask : dcam4_sys::DCAMWAIT_EVENT_DCAMWAIT_CAPEVENT_FRAMEREADY,
		// 		timeout : DCAMWAIT_TIMEOUT_DCAMWAIT_TIMEOUT_INFINITE
		// 	};
		// 	dcam_check(dcam4_sys::dcamwait_start(wait_open.hwait, &mut wait))?;
		// };
		Ok(())
		//DCAMWAIT_CAPEVENT.FRAMEREADY, timeout_millisec
		//dcamwait_start
		//dcambuf_copyframe(...)
        // std::mem::transmute<&Image, &self.image_buffer.as_ref().pixels()
		// self.image_buffer.as_ref()
		// unsafe{
		// 	std::slice::from_raw_parts(
		// 		std::mem::transmute::<*const u8, *const u16>(self.image_buffer.data.as_ptr()),
		// 		self.image_buffer.data.len()/2
		// 	)}
    }

	pub fn stop_stream(&self) -> Result<(), dcam::Error> {
		unsafe{
			dcam_check(dcam4_sys::dcamcap_stop( self.handle ))?;
			dcam_check(dcam4_sys::dcambuf_release(self.handle, dcam4_sys::DCAM_ATTACHKIND_DCAMBUF_ATTACHKIND_FRAME))
		}
	}

	pub fn frames_produced(&self) -> Result<i32, dcam::Error> {
		let mut transfer_info = dcam4_sys::DCAMCAP_TRANSFERINFO{
			size : std::mem::size_of::<dcam4_sys::DCAMCAP_TRANSFERINFO>() as i32,
			iKind : DCAMCAP_TRANSFERKIND_DCAMCAP_TRANSFERKIND_FRAME,
			nNewestFrameIndex : 0,
			nFrameCount : 0
		};
		unsafe{dcam_check(dcam4_sys::dcamcap_transferinfo(self.handle, &mut transfer_info))?;}
		Ok(transfer_info.nFrameCount)
	}

	pub fn wait_for_next_frame(&self) -> Result<(), dcam::Error> {
		unsafe{
			let mut wait_open = dcam4_sys::DCAMWAIT_OPEN{
				size : std::mem::size_of::<dcam4_sys::DCAMWAIT_OPEN>() as i32,
				supportevent : 0,
				hwait : std::ptr::null_mut(),
				hdcam : self.handle
			};
			dcam_check(dcam4_sys::dcamwait_open(&mut wait_open))?;
			let mut wait = dcam4_sys::DCAMWAIT_START{
				size : std::mem::size_of::<dcam4_sys::DCAMWAIT_START>() as i32,
				eventhappened : 0,
				eventmask : dcam4_sys::DCAMWAIT_EVENT_DCAMWAIT_CAPEVENT_FRAMEREADY,
				timeout : DCAMWAIT_TIMEOUT_DCAMWAIT_TIMEOUT_INFINITE
			};
			dcam_check(dcam4_sys::dcamwait_start(wait_open.hwait, &mut wait))?;
			//TODO: reuse this handle
			dcam_check(dcam4_sys::dcamwait_close(wait_open.hwait))?
		};
		// self.frames_produced()
		Ok(())
	}
	pub fn wait_for_next_frame_timeout(&self, timeout_ms : i32) -> Result<(), dcam::Error> {
		unsafe{
			let mut wait_open = dcam4_sys::DCAMWAIT_OPEN{
				size : std::mem::size_of::<dcam4_sys::DCAMWAIT_OPEN>() as i32,
				supportevent : 0,
				hwait : std::ptr::null_mut(),
				hdcam : self.handle
			};
			dcam_check(dcam4_sys::dcamwait_open(&mut wait_open))?;
			let mut wait = dcam4_sys::DCAMWAIT_START{
				size : std::mem::size_of::<dcam4_sys::DCAMWAIT_START>() as i32,
				eventhappened : 0,
				eventmask : dcam4_sys::DCAMWAIT_EVENT_DCAMWAIT_CAPEVENT_FRAMEREADY,
				timeout : timeout_ms
			};
			dcam_check(dcam4_sys::dcamwait_start(wait_open.hwait, &mut wait))?;
			//TODO: reuse this handle
			dcam_check(dcam4_sys::dcamwait_close(wait_open.hwait))?
		};
		// self.frames_produced()
		Ok(())
	}
}
